from fastapi import FastAPI
from fastapi.responses import StreamingResponse, JSONResponse, Response
from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from picamera2.outputs import FfmpegOutput
import io
import os
import uvicorn
import config as cfg
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import time
from datetime import datetime
import atexit
import cv2
import numpy as np

cam = None
camera_running = False
current_fps = 0
is_recording = False
recording_encoder = None
recording_output = None
recording_path = None
stream_format = cfg.DEFAULT_FORMAT

def start_camera():
    global cam, camera_running

    if camera_running:
        return True

    for attempt in range(3):
        try:
            cam = Picamera2()

            camera_config = cam.create_preview_configuration(
                main={
                    "size": (cfg.STREAM_WIDTH, cfg.STREAM_HEIGHT),
                    "format": stream_format
                },
            )

            cam.configure(camera_config)
            cam.start()

            time.sleep(0.5)

            camera_running = True
            print("Camera started successfully")
            return True

        except Exception as e:
            print(f"Camera start attempt {attempt + 1} failed: {e}")

            if cam:
                try:
                    cam.close()
                except:
                    pass
                cam = None

            time.sleep(1)

    print("Failed to start camera after 3 attempts")
    return False


def stop_camera():
    global cam, camera_running

    if not camera_running:
        return True

    camera_running = False

    time.sleep(0.2)

    if cam:
        try:
            cam.stop()
            cam.close()
        except Exception as e:
            print(f"Error stopping camera: {e}")
        cam = None

    print("Camera stopped")
    return True


atexit.register(stop_camera)


def generate_frames():
    global camera_running, current_fps

    last_time = time.time()
    encode_param = [cv2.IMWRITE_JPEG_QUALITY, 40]

    while camera_running:
        try:
            frame = cam.capture_array()

            if stream_format == "YUV420":
                frame = cv2.cvtColor(frame, cv2.COLOR_YUV420p2RGB)
            elif stream_format == "BGR888":
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            elif stream_format in ["RGB888", "XRGB8888"]:
                pass
            elif stream_format == "YUYV":
                frame = cv2.cvtColor(frame, cv2.COLOR_YUV2RGB_YUYV)
            elif stream_format == "UYVY":
                frame = cv2.cvtColor(frame, cv2.COLOR_YUV2RGB_UYVY)
            elif stream_format == "NV12":
                frame = cv2.cvtColor(frame, cv2.COLOR_YUV2RGB_NV12)
            elif stream_format == "NV21":
                frame = cv2.cvtColor(frame, cv2.COLOR_YUV2RGB_NV21)
            elif stream_format == "R8":
                frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)

            _, jpeg = cv2.imencode('.jpg', frame, encode_param)

            yield (
                    b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n'
            )
        except Exception as e:
            print(f"Frame capture error: {e}")
            break

        now = time.time()
        elapsed = now - last_time
        current_fps = round(1.0 / elapsed) if elapsed > 0 else 0
        last_time = now


app = FastAPI()


@app.post("/api/start")
async def api_start():
    success = start_camera()

    if success:
        return {"success": True, "running": True}
    else:
        return JSONResponse(
            {"success": False, "running": False, "error": "Failed to start camera"},
            status_code=500
        )


@app.post("/api/stop")
async def api_stop():
    stop_camera()
    return {"success": True, "running": False}


@app.get("/api/status")
async def api_status():
    return {"running": camera_running, "fps": current_fps, "width": cfg.STREAM_WIDTH, "height": cfg.STREAM_HEIGHT}


@app.post("/api/photo")
async def api_photo():
    if not camera_running:
        return JSONResponse({"error": "Camera not running"}, status_code=503)

    try:
        still_config = cam.create_still_configuration(
            main={"size": (cfg.PHOTO_WIDTH, cfg.PHOTO_HEIGHT)}
        )

        # AI bug fix <<<
        buffer = io.BytesIO()
        cam.switch_mode_and_capture_file(still_config, buffer, format='jpeg')

        buffer.seek(0)
        frame = cv2.imdecode(np.frombuffer(buffer.read(), np.uint8), cv2.IMREAD_COLOR)

        timestamp = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        cv2.putText(frame, timestamp, (60, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 7)
        cv2.putText(frame, timestamp, (60, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 3)

        _, jpeg = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, cfg.JPEG_QUALITY])

        # >>> AI bug fix

        return Response(content=jpeg.tobytes(), media_type="image/jpeg")
    except Exception as e:
        print(f"Photo capture error: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)


@app.post("/api/record/start")
async def api_start_video():
    global is_recording, recording_encoder, recording_output, recording_path

    if not camera_running:
        return JSONResponse({"error": "Camera not running"}, status_code=503)
    if is_recording:
        return JSONResponse({"error": "Camera already recording"}, status_code=400)

    try:
        recording_path = f"/tmp/video_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"

        recording_encoder = H264Encoder(bitrate=10000000)
        recording_output = FfmpegOutput(recording_path)

        cam.start_recording(recording_encoder, recording_output)
        is_recording = True

        return {"success": True, "recording": True}
    except Exception as e:
        print(f"Recording start error: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)


@app.post("/api/record/stop")
async def api_stop_video():
    global is_recording, recording_encoder, recording_output, recording_path

    if not is_recording:
        return JSONResponse({"error": "Not recording"}, status_code=400)

    try:

        cam.stop_recording()
        is_recording = False

        with open(recording_path, "rb") as f:
            video_data = f.read()

        os.remove(recording_path)
        recording_path = None

        return Response(content=video_data, media_type="video/mp4")
    except Exception as e:
        print(f"Recording stop error: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)


@app.post("/api/format/{format_name}")
async def api_switch_format(format_name: str):
    global stream_format

    if format_name not in cfg.STREAM_FORMATS:
        return JSONResponse({"error": "Stream format not supported"}, status_code=503)

    stream_format = format_name

    if camera_running:
        stop_camera()
        start_camera()
    return {"success": True, "format": stream_format}


@app.get("/api/formats")
async def api_get_formats():
    return {"formats": cfg.STREAM_FORMATS, "current": stream_format}


@app.get("/stream")
async def video_stream():
    if not camera_running:
        return JSONResponse(
            {"error": "Camera is not running. Call /api/start first."},
            status_code=503
        )

    return StreamingResponse(
        generate_frames(),
        media_type='multipart/x-mixed-replace; boundary=frame'
    )


@app.on_event("shutdown")
async def shutdown():
    stop_camera()


frontend_path = Path(__file__).parent.parent / "frontend"
app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="frontend")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
