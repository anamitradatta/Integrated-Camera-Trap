import paho.mqtt.publish as publish
from picamera import PiCamera
from time import sleep
from gpiozero import MotionSensor
import os
import shutil

#Author: Anamitra Datta

#Master Publisher Code for single sensor Photo triggering. 
#When the sensor on the master Pi is activated, it will send a message to all slaves devices via MQTT to take a photo

path = "/home/pi/cameraTrapPhotos/" #photos directory
access_rights = 0o777 #permissions for directory , 777 means everyone can read, write, and execute a file

#create a directory if one does not exist for the camera trap photos
if(os.path.isdir(path)==False):
	os.mkdir(path,access_rights)
#else, remove all photos and photo sets currently in the directory
else:
	for fname in os.listdir(path):
		shutil.rmtree(path+fname)

MQTT_SERVER = "localhost" #master Pi IP address
MQTT_PATH = "test" #topic name for MQTT

camera = PiCamera() #use camera
pir = MotionSensor(4) #use motion sensor
photoNum = 1 #current Photo (set) number
delay = 30 #amount of time in seconds to rest after a photo session (should be greater than 30 seconds)

#runs continously until termination by user
while True:
	#Rests for a few seconds to FTP all photos from slave devices and to prevent multiple photos to be taken in a small time frame
	print("Photo synchroniztion program: master device running")
	print("Resting the program for a few seconds...")
	sleep(delay)
	print("Done resting")
	message = "Motion Not Detected" #initalizing message to send via MQTT
	startdetection = False

    #Wait until motion is detected to start photo session
	while True:
		if pir.motion_detected == False and startdetection == False:
			startdetection = True
		sleep(1)
		print(pir.motion_detected)
		if startdetection== True:
			if pir.motion_detected == True:
				#motion detected, change message to "take photo", send to all slave devices, attach current set number
				message = "Take Synced Photo " + str(photoNum)
				break;

	print("Motion has been detected. Taking camera 1 Photo" + str(photoNum))

	#MQTT, send message to all slaves in network to take a photo
	publish.single(MQTT_PATH, message, hostname=MQTT_SERVER)

	path = '/home/pi/cameraTrapPhotos/set' + str(photoNum) +  '/' #path for photo

    #make a directory for the current session to store photos in 
	try:
		os.mkdir(path,access_rights)
	except OSError:
		print("creation of the directory %s failed" % path)
	else:
		print("successfully created the directory %s" % path)

    #set up photo and camera settings
	filename = 'set'+str(photoNum)+'_camera1.jpg'
	camera.resolution=(3280,2464)
	camera.shutter_speed = 30000

	#Take Photo
	camera.capture(path+filename)

	#End of Photo session
	print("Camera 1 photo number "+ str(photoNum) + " taken")

	#go to next photo session
	photoNum = photoNum + 1
