from picamera import PiCamera
from time import sleep
import datetime

camera = PiCamera()
camera.resolution=(3280,2464)
camera.start_preview()
sleep(5)
date = datetime.datetime.now().strftime("%m_%d_%Y_%H_%M_%S_%f")
camera.capture('/home/pi/Desktop/cameraTrapPhotos/' + date +'.jpg')
camera.stop_preview()

