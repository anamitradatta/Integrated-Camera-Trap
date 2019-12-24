import picamera as picam
from time import sleep

with picam.PiCamera() as mycam:
    print('Starting...')
    mycam.resolution = (3280,2464) #8 MegaPixels
    mycam.exposure_mode = 'sports'
    mycam.start_preview()
    sleep(5)

    mycam.capture('/home/pi/Desktop/cameraTrapPhotos/ShutterTestSport.jpg')
    mycam.stop_preview()