from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from picamera2 import Picamera2
import io
import uvicorn
import config as cfg
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import time
import atexit

cam = None


def init_camera():
    global cam
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
            return
        except Exception as e:
            print(f"Camera init attempt {attempt + 1} failed: {e}")
            if cam:
                try:
                    cam.close()
                except:
                    pass
            time.sleep(1)
    raise RuntimeError("Failed to initialize camera")


def cleanup():
    global cam
    if cam:
        try:
            cam.stop()
            cam.close()
        except:
            pass


atexit.register(cleanup)

init_camera()


def generate_frames():
    frame_interval = 1.0 / 30
    while True:
        start = time.time()
        stream = io.BytesIO()
        try:
            cam.capture_file(stream, format='jpeg')
            frame = stream.getvalue()
            yield (
                    b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n'
            )
        finally:
            stream.close()

        elapsed = time.time() - start
        if elapsed < frame_interval:
            time.sleep(frame_interval - elapsed)


app = FastAPI()


@app.get("/stream")
async def video_stream():
    return StreamingResponse(
        generate_frames(),
        media_type='multipart/x-mixed-replace; boundary=frame'
    )


@app.on_event("shutdown")
async def shutdown():
    cleanup()


frontend_path = Path(__file__).parent.parent / "frontend"
app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="frontend")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
