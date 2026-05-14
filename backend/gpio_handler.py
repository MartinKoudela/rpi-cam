from gpiozero import MotionSensor
import threading
import recorder
import camera
import config as cfg

pir = None
_debounce_timer = None


def _on_motion():
    global _debounce_timer
    if _debounce_timer:
        _debounce_timer.cancel()
        _debounce_timer = None
    if camera.camera_running:
        recorder.start_recording()


def _on_no_motion():
    global _debounce_timer
    _debounce_timer = threading.Timer(cfg.PIR_DEBOUNCE, recorder.stop_recording)
    _debounce_timer.start()


def start_pir():
    global pir
    pir = MotionSensor(17)
    pir.when_motion = _on_motion
    pir.when_no_motion = _on_no_motion


def stop_pir():
    global pir, _debounce_timer
    if _debounce_timer:
        _debounce_timer.cancel()
    if pir:
        pir.close()
        pir = None
