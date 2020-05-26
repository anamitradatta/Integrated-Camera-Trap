import paho.mqtt.client as mqtt
from picamera import PiCamera
from time import sleep
import socket
import datetime
from ftplib import FTP
import os
import shutil
import sys

#Author: Anamitra Datta

#slave client code for single sensor photo triggering.
#When this device gets a message from the master Pi to take a photo
#take a photo and ftp it to the main pi

MQTT_SERVER = "192.168.5.101" #IP address of main pi
MQTT_PATH = "test" #mqtt topic for CT program
path = '/home/pi/cameraTrapPhotos/' #directory for photos
camera = PiCamera() #use the camera
cameraNum = 3 #camera number, needs to be different for each pi
access_rights = 0o777 #permissions for directory

#create a directory if one does not exist for the camera trap photos
if(os.path.isdir(path)==False):
	os.mkdir(path,access_rights)
#else, remove all photos and photo sets currently in the directory
else:
	for fname in os.listdir(path):
		shutil.rmtree(path+fname)

#method to subscribe to MQTT topic
def on_connect(client, userdata, flags, rc):
    #result code 0 = successful
    print("Connected with result code "+str(rc))
    print("Started the photo synchronization program on slave "+ str(cameraNum) + " Waiting for a signal from the master module")
    # Subscribing in on_connect() - if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(MQTT_PATH)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    word_list = (msg.payload).split()
    #if master pi asks to take a photo, take a photo and ftp it to main pi
    if word_list[0] == "Take":
        print("Received message: " + str(msg.payload))
        photoNum = int(word_list[-1]) #get current photo session number
        path = '/home/pi/cameraTrapPhotos/set' + str(photoNum) + '/'
        access_rights = 0o777 #permissions for directory

        #make directory for current photo session
        try:
            os.mkdir(path,access_rights)
        except OSError:
            print("creation of the directory %s failed" % path)
        else:
            print("sucessfully created the directory %s" % path)

        #set up camera and file parameters
        photoName = 'set' + str(photoNum) + '_camera' + str(cameraNum) + '.jpg'
        camera.resolution = (3240,2464)
        camera.shutter_speed = 30000

        #take photo
        camera.capture(path + photoName)
        print("Photo Number", photoNum, " taken on Slave " + str(cameraNum))

        #FTP to master pi
        print("Moving from Cam " + str(cameraNum) +" to Master")
        ftp = FTP(MQTT_SERVER)
        ftp.login('pi','raspberry')
        pathMaster = '/home/pi/cameraTrapPhotos/set' + str(photoNum) + '/'
        ftp.cwd(pathMaster)
        try:
            file = open(path + photoName,'rb')
        except OSError:
            print("could not open file")
        ftp.storbinary('STOR ' + pathMaster + photoName, file)
        print("finished moving photo from Cam " + str(cameraNum)+ " to master")

        file.close()
        ftp.quit()
        print("closed ftp connection")

# Create an MQTT client and attach our routines to it.
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_SERVER, 1883) #connect to mqtt server on master pi, use port 1883, port for MQTT

# Process network traffic and dispatch callbacks. This will also handle
# reconnecting.
client.loop_forever()
