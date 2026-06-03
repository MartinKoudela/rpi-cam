from picamera2 import Picamera2
from datetime import datetime
import asyncio
import time
import io
import cv2
import numpy as np
import atexit
import config as cfg

cam = None
camera_running = False
current_fps = 0
_last_frame_time = 0.0


def start_camera():
    global cam, camera_running

    if camera_running:
        return True

    for attempt in range(3):
        try:
            cam = Picamera2()
            camera_config = cam.create_preview_configuration(
                main={"size": (cfg.STREAM_WIDTH, cfg.STREAM_HEIGHT), "format": "BGR888"},
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


def capture_frame():
    global current_fps, _last_frame_time

    now = time.time()
    if _last_frame_time > 0:
        current_fps = round(1.0 / (now - _last_frame_time)) if now > _last_frame_time else 0
    _last_frame_time = now

    frame = cv2.cvtColor(cam.capture_array(), cv2.COLOR_RGB2BGR)
    _, jpeg = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 40])
    return jpeg.tobytes()


async def generate_frames():
    frame_interval = 1.0 / 20

    while camera_running:
        t = time.time()
        try:
            frame = cv2.cvtColor(await asyncio.to_thread(cam.capture_array), cv2.COLOR_RGB2BGR)
            _, jpeg = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 40])
            yield b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n'
        except Exception as e:
            print(f"Frame capture error: {e}")
            break

        sleep = frame_interval - (time.time() - t)
        if sleep > 0:
            await asyncio.sleep(sleep)


def take_photo():
    still_config = cam.create_still_configuration(
        main={"size": (cfg.PHOTO_WIDTH, cfg.PHOTO_HEIGHT)}
    )

    buffer = io.BytesIO()
    cam.switch_mode_and_capture_file(still_config, buffer, format='jpeg')
    buffer.seek(0)

    frame = cv2.imdecode(np.frombuffer(buffer.read(), np.uint8), cv2.IMREAD_COLOR)

    timestamp = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    cv2.putText(frame, timestamp, (60, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 7)
    cv2.putText(frame, timestamp, (60, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 3)

    _, jpeg = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, cfg.JPEG_QUALITY])
    return jpeg.tobytes()