from fastapi import FastAPI
from fastapi.responses import StreamingResponse, JSONResponse, Response
from picamera2 import Picamera2
import io
import uvicorn
import config as cfg
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import time
import atexit

# TODO: record with cv2 fram info

cam = None
camera_running = False


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
                    "format": cfg.STREAM_FORMAT
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
    global camera_running

    frame_interval = 1.0 / 30

    while camera_running:
        start = time.time()

        stream = io.BytesIO()

        try:
            cam.capture_file(stream, format='jpeg')
            frame = stream.getvalue()
            yield (
                    b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n'

            )
        except Exception as e:
            print(f"Frame capture error: {e}")
            break
        finally:
            stream.close()

        elapsed = time.time() - start
        if elapsed < frame_interval:
            time.sleep(frame_interval - elapsed)


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
    return {"running": camera_running}


@app.post("/api/photo")
async def api_photo():
    if not camera_running:
        return JSONResponse({"error": "Camera not running"}, status_code=503)

    try:
        still_config = cam.create_still_configuration(
            main={"size": (cfg.PHOTO_WIDTH, cfg.PHOTO_HEIGHT)}
        )

        photo_stream = io.BytesIO()

        cam.switch_mode_and_capture_file(still_config, photo_stream, format='jpeg')

        return Response(content=photo_stream.getvalue(), media_type="image/jpeg")

    except Exception as e:
        print(f"Photo capture error: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)


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
