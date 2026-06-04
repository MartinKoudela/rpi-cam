from picamera2.encoders import H264Encoder
from picamera2.outputs import CircularOutput, FfmpegOutput
from pathlib import Path
from datetime import datetime
import config as cfg
import camera

is_recording = False
_recording_path = None
_circular = None
_encoder = None


def start_buffer():
    global _circular, _encoder
    _encoder = H264Encoder(bitrate=cfg.VIDEO_BITRATE)
    _circular = CircularOutput(buffersize=cfg.PIR_PREROLL_SECONDS * cfg.VIDEO_BITRATE // 8)
    camera.cam.start_recording(_encoder, _circular)


def stop_buffer():
    global _circular, _encoder, is_recording, _recording_path
    if is_recording and _circular:
        _circular.stop()
        _circular.fileoutput = None
        is_recording = False
        _recording_path = None
    try:
        camera.cam.stop_recording()
    except Exception:
        pass
    _circular = None
    _encoder = None


def start_recording():
    global is_recording, _recording_path
    if is_recording or _circular is None:
        return False

    videos_dir = Path(cfg.VIDEOS_DIR)
    videos_dir.mkdir(parents=True, exist_ok=True)
    _recording_path = str(videos_dir / f"video_{datetime.now().strftime('%Y-%m-%d_%H:%M:%S')}.mp4")

    _circular.fileoutput = FfmpegOutput(_recording_path)
    _circular.start()
    is_recording = True
    print(f"Recording started: {_recording_path}")
    return True


def stop_recording():
    global is_recording, _recording_path
    if not is_recording or _circular is None:
        return None

    _circular.stop()
    _circular.fileoutput = None
    is_recording = False

    path = _recording_path
    _recording_path = None
    print(f"Recording saved: {path}")
    return path