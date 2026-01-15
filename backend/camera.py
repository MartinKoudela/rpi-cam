from picamera2 import Picamera2
from time import sleep

cam = Picamera2()
cam.start()
cam.capture_file("test.jpg")
print("Image saved")
cam.stop()