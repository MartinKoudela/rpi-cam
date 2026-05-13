from gpiozero import MotionSensor
import time

pir = MotionSensor(17)
print("Zatím žádný pohyb...")

while True:
    if pir.motion_detected:
        print("Pohyb!")
    else:
        print("Žádný pohyb.")
    time.sleep(0.5)