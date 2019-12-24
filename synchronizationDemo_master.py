import paho.mqtt.publish as publish
from picamera import PiCamera
from time import sleep
from gpiozero import MotionSensor
import random
import os

#Timing Synchronization Demo Code

camera = PiCamera()
MQTT_SERVER = "localhost"
MQTT_PATH = "test"



startInput = raw_input ("\nStart Code? (y/n): ")
photoNum = 1

if (os.path.isdir('/home/pi/Desktop/synchTestPhotos') == False):
    print "Make Sure there is a synchTestPhotos Folder"
    startInput = "n"

while startInput == "y":
    waitTime = input ("\nHow Many Seconds Do You Want to Wait? (Enter 0 for random number): ")
    
    if (waitTime == 0):
        waitTime = random.randint(5, 15)
    
    print "Waiting ", waitTime, "secs"
    for i in reversed(xrange(waitTime)):
        print i+1, "seconds"
        sleep(1)
    print('\nDone Waiting \n')
    
    message = "Take Synced Photo " + str(photoNum)
    
    #Send out message to Take Photo
    publish.single(MQTT_PATH, message, hostname=MQTT_SERVER)
    
    #Take Photo
    word_list = message.split()
    if (word_list[0] == "Take"):
        photoNum = int(word_list[-1])
    
        path = '/home/pi/Desktop/synchTestPhotos/'
        photoName = 'synchPhotoCam1_' + str(photoNum) + '.jpg'
    
	camera.resolution = (3240, 2464)
        camera.shutter_speed = 30000
        camera.start_preview()
        sleep(1)
        camera.capture(path + photoName)
        camera.stop_preview()
    
        print "Photo Number", photoNum, " taken"
    
        photoNum += 1
    
    #MQTT
    #FTP


    

