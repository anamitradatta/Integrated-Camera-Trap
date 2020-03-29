from picamera import PiCamera
from time import sleep

camera = PiCamera()
camera.resolution=(3280,2464)
path = '/home/pi/test_photo.jpg'
camera.start_preview()
camera.capture(path)
camera.stop_preview()

