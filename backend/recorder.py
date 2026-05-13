from picamera2.encoders import H264Encoder
from picamera2.outputs import FfmpegOutput
from pathlib import Path
from datetime import datetime
import config as cfg
import camera

is_recording = False
_recording_path = None


def start_recording():
    global is_recording, _recording_path

    if not camera.camera_running or is_recording:
        return False

    videos_dir = Path(cfg.VIDEOS_DIR)
    videos_dir.mkdir(parents=True, exist_ok=True)

    _recording_path = str(videos_dir / f"video_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4")

    encoder = H264Encoder(bitrate=10000000)
    output = FfmpegOutput(_recording_path)
    camera.cam.start_recording(encoder, output)

    is_recording = True
    print(f"Recording started: {_recording_path}")
    return True


def stop_recording():
    global is_recording, _recording_path

    if not is_recording:
        return None

    camera.cam.stop_recording()
    is_recording = False

    path = _recording_path
    _recording_path = None
    print(f"Recording saved: {path}")
    return path