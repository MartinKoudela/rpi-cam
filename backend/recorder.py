from pathlib import Path
from datetime import datetime
import threading
import subprocess
import time
import cv2
import config as cfg
import camera

_RECORD_FPS = 15

is_recording = False
_recording_path = None
_ffmpeg_proc = None
_record_thread = None
_stop_event = None


def _capture_loop(stop_event):
    interval = 1.0 / _RECORD_FPS
    while not stop_event.is_set():
        t = time.time()
        if camera.camera_running and camera.cam:
            try:
                raw = camera.cam.capture_array()
                frame = cv2.cvtColor(raw, cv2.COLOR_RGB2BGR)
                _, jpeg = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
                if _ffmpeg_proc and _ffmpeg_proc.poll() is None:
                    _ffmpeg_proc.stdin.write(jpeg.tobytes())
            except Exception:
                pass
        elapsed = time.time() - t
        sleep = interval - elapsed
        if sleep > 0:
            time.sleep(sleep)


def start_recording():
    global is_recording, _recording_path, _ffmpeg_proc, _record_thread, _stop_event
    if is_recording or not camera.camera_running:
        return False

    videos_dir = Path(cfg.VIDEOS_DIR)
    videos_dir.mkdir(parents=True, exist_ok=True)
    _recording_path = str(videos_dir / f"video_{datetime.now().strftime('%Y-%m-%d_%H:%M:%S')}.mp4")

    try:
        _ffmpeg_proc = subprocess.Popen(
            [
                'ffmpeg', '-y',
                '-f', 'image2pipe', '-vcodec', 'mjpeg',
                '-framerate', str(_RECORD_FPS),
                '-i', 'pipe:0',
                '-vcodec', 'libx264', '-preset', 'ultrafast', '-pix_fmt', 'yuv420p',
                '-r', str(_RECORD_FPS),
                _recording_path,
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception as e:
        print(f"Failed to start ffmpeg: {e}")
        _recording_path = None
        return False

    _stop_event = threading.Event()
    _record_thread = threading.Thread(target=_capture_loop, args=(_stop_event,), daemon=True)
    _record_thread.start()
    is_recording = True
    print(f"Recording started: {_recording_path}")
    return True


def stop_recording():
    global is_recording, _recording_path, _ffmpeg_proc, _record_thread, _stop_event
    if not is_recording:
        return None

    is_recording = False
    path = _recording_path
    _recording_path = None

    if _stop_event:
        _stop_event.set()
    if _record_thread:
        _record_thread.join(timeout=3)
        _record_thread = None
    _stop_event = None

    if _ffmpeg_proc:
        try:
            _ffmpeg_proc.stdin.close()
            _ffmpeg_proc.wait(timeout=30)
        except Exception:
            _ffmpeg_proc.kill()
        _ffmpeg_proc = None

    print(f"Recording saved: {path}")
    return path