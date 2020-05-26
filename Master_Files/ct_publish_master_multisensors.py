import paho.mqtt.publish as publish
from picamera import PiCamera
from time import sleep
import time
from gpiozero import MotionSensor
import socket
import datetime
import os
import shutil
import commands

#Authors:
#Anamitra Datta
#Minting Chen

#Master Publisher code for multiple sensors photo triggering
#Continously and periodically polls all devices in the network to knwo about their sensor values
#If a certain percentage of sensors are true in the network, then motion is detected
#Then, start the photo session process by sending a message to all slave devices to take a photo

print("Started master multisensor photo sync program")

MQTT_SERVER = "localhost" #master Pi IP address
MQTT_PATH = "test" #topic name for MQTT
path = '/home/pi/cameraTrapPhotos/'
pir = MotionSensor(4) #use motion sensor
camera = PiCamera() #use camera
access_rights = 0o777

#create a directory if one does not exist for the camera trap photos
if(os.path.isdir(path)==False):
	os.mkdir(path,access_rights)
#else, remove all photos and photo sets currently in the directory
else:
	for fname in os.listdir(path):
		shutil.rmtree(path+fname)

IPAddr = commands.getoutput("hostname -I") #get Pi's own IP address

threshold = 0.67 #threshold for taking photo, percent of sensors that need to be true to take a photo, configurable
photoNum = 1 #current set/photo number
delay = 30 #amount of time in seconds to rest after a photo session (should be greater than 30 seconds)

#set socket for listening to slave pis
s = socket.socket()
s.settimeout(10) #set timeout for few seconds, enough to read sensor data from all slave Pis
s.bind(('',12345)) #bind the socket to a unused undesignated port

#run continously until terminated by user
while True:
	sensorlist = [] #list of all devices by their ip addresses and their sensor readings
	print("Resting...")
	sleep(delay)
	print("Starting")
	message = "Info"
	publish.single(MQTT_PATH,message,hostname=MQTT_SERVER) #send message get info about slave sensors

    #put sensor state of master pi in sensor list
	if(pir.motion_detected==True):
		sensorlist.append([str(IPAddr).rstrip(),str(True)])
	else:
		sensorlist.append([str(IPAddr).rstrip(),str(False)])

    #listen for incoming connections
	s.listen(5)
	print("Socket is listening")

    #get data from slave pis by listening to socket and parse it and add it to sensor list
	while True:
		try:
			c,addr = s.accept() #accept connections from slave pis
			print('Got connection from', addr)
			receivedInfo = str(c.recv(1024))

            #parse data and add it to the sensor list
			splitInfo = receivedInfo.split()
			receivedIP = splitInfo[0]
			receivedSensor = splitInfo[1]
			sensorlist.append([receivedIP,receivedSensor])
			c.close()

		except socket.timeout:
			break

	#list of all devices and their sensor readings
	for x in sensorlist:
		print(x)

    #calculate percentage of sensors that show true
	numSensors = float(0)
	numTrue = float(0)
	for i, element in enumerate(sensorlist):
		numSensors = numSensors + 1
		if element[1] == "True":
			numTrue = numTrue + 1
	ratio = numTrue/numSensors
	print("ratio: " + str(ratio))

    #if ratio is above the threshold, start a photo session
	if(ratio>threshold):
		#Send MQTT message to slaves to take photo and start photo
		message = "Take Synced Photo " + str(photoNum)
		publish.single(MQTT_PATH,message,hostname=MQTT_SERVER)
		ctpath = '/home/pi/cameraTrapPhotos/set' + str(photoNum) +  '/'
		access_rights = 0o777 #permissions for directory
        #make directory for current photo session
		try:
			os.mkdir(ctpath,access_rights)
		except OSError:
			print("creation of the directory %s failed" % ctpath)
		else:
			print("successfully created the directory %s" % ctpath)

        #set camera and file parameters
		filename = 'set'+str(photoNum)+'_camera1.jpg'
		camera.resolution=(3280,2464)
		camera.shutter_speed = 30000

		#Take Photo
		camera.capture(ctpath+filename)
		#End of Photo session

		print("Camera 1 photo number "+ str(photoNum) + " taken")
		#go to next photo session
		photoNum = photoNum + 1
