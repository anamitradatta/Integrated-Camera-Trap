import paho.mqtt.client as mqtt
from picamera import PiCamera
from time import sleep
import socket
import datetime
from ftplib import FTP
import os
import shutil
import commands
from gpiozero import MotionSensor

#Authors: 
#Anamitra Datta
#Minting Chen

MQTT_SERVER = "192.168.5.101" #IP adress of master pi
MQTT_PATH = "test" #mqtt topic for CT program

pir=MotionSensor(4) #use motion sensor
camera = PiCamera() #use camera
path = '/home/pi/Desktop/cameraTrapPhotos/' #directory to store photos on

#method to subscribe to MQTT topic
def on_connect(client, userdata, flags, rc):
	#result code 0 = success
	print("Connected with result code "+str(rc))
	print "Started multisensors photo synchronization program on slave 2"
    # Subscribing in on_connect() - if we lose the connection and
    # reconnect then subscriptions will be renewed.
	client.subscribe(MQTT_PATH)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
	wordlist = (msg.payload).split()
	
	#send info about IP address and sensor reading
	if(wordlist[0]=="Info"): #send sensor status to main pi for consensus
		IPAddr = commands.getoutput("hostname -I") #ip addres of slave pi

        #set up socket connection with master pi to send sensor status
		s = socket.socket()
		port = 12345 #connect to master multisensor port 
		s.connect((MQTT_SERVER,port))
        
		if(pir.motion_detected==True):
			s.sendall(str(IPAddr) + "True")
		else:
			s.sendall(str(IPAddr) + "False")
		s.close()

	if(wordlist[0]=="Take"): #take photo and send it to main pi
		photoNum = int(wordlist[-1])
		path = '/home/pi/Desktop/cameraTrapPhotos/set' + str(photoNum) + '/'
		access_rights = 0o777
        
        #make directory for current photo session
		try:
			os.mkdir(path,access_rights)
		except OSError:
			print("creation of the directory %s failed" % path)
		else:
			print("sucessfully created the directory %s" % path)
            
        #set up camera and file parameters
		photoName = 'set' + str(photoNum) + '_camera2.jpg'
		camera.resolution = (3240,2464)
		camera.shutter_speed = 30000
        
        #take photo
		camera.capture(path + photoName)
		print("Photo Number " +  str(photoNum) +  " taken on Slave 2")

		#FTP to master pi
		print("Moving from Cam2 to Master")
		ftp = FTP(MQTT_SERVER)
		ftp.login('pi','raspberry')
		pathMaster = '/home/pi/cameraTrapPhotos/set' + str(photoNum) + '/'
		ftp.cwd(pathMaster)

		try:
			file = open(path + photoName,'rb')
		except OSError:
			print('couldnt open file')
            
		ftp.storbinary('STOR ' + pathMaster + photoName, file)
		print("Finished moving photo from Cam2 to master")
		file.close()
		ftp.quit()
        print("closed FTP connection")

# Create an MQTT client and attach our routines to it.
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_SERVER, 1883) #connect to mqtt server on master pi at port 1883, designated for MQTT protocol

# Process network traffic and dispatch callbacks. This will also handle
# reconnecting.
client.loop_forever()
