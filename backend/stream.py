from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from picamera2 import Picamera2
import io
import uvicorn
import config as cfg

cam = Picamera2()

camera_config = cam.create_preview_configuration(
    main={
        "size": (cfg.STREAM_WIDTH, cfg.STREAM_HEIGHT),
        "format": cfg.STREAM_FORMAT
    },
)

cam.stop()
cam.configure(camera_config)
cam.start()


def generate_frames():
    while True:
        stream = io.BytesIO()
        cam.capture_file(stream, format='jpeg')
        frame = stream.getvalue()

        yield (
                b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n'
        )


app = FastAPI()


@app.get("/stream")
async def video_stream():
    return StreamingResponse(
        generate_frames(),
        media_type='multipart/x-mixed-replace; boundary=frame'
    )


uvicorn.run(app, host="0.0.0.0", port=8000)
