import paho.mqtt.client as mqtt
from picamera import PiCamera
from time import sleep
import socket
import datetime
from ftplib import FTP
import os

MQTT_SERVER = "192.168.1.143"
MQTT_PATH = "test"

camera = PiCamera()

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
	print("Connected with result code "+str(rc))
	if(os.path.isdir('/home/pi/Desktop/walkTestPhotos_Slave2') == False):
            print "Make Sure there's a walkTestPhotos_Slave2 folder"

    # Subscribing in on_connect() - if we lose the connection and
    # reconnect then subscriptions will be renewed.
	client.subscribe(MQTT_PATH)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(str(msg.payload))
    
    word_list = (msg.payload).split()
    
    brightnessInput = int(word_list[-1])
    shutterInput = int(word_list[-3])
    delayInput = float(word_list[-5])
    photoNum = word_list[-7]

    camera.exposure_mode = 'sports'
    
    if (word_list[0] == "Motion"):
        path = '/home/pi/Desktop/walkTestPhotos_Slave2/'
        photoName = 'walkTest_cam2_photo' + str(photoNum) + '.jpg'
        camera.shutter_speed = shutterInput*1000
        camera.resolution = (3280, 2464)
	camera.brightness = brightnessInput

        camera.start_preview()
        sleep(delayInput)
        camera.capture(path + photoName)
        camera.stop_preview()
        print "Photo Number ", photoNum, " taken on Slave 2"
        
        print "Moving from Cam2 to Master"
        ftp = FTP(MQTT_SERVER)
        login_response = ftp.login('pi','raspberry')
        
        pathMaster = '/home/pi/Desktop/walkTestPhotos/'
        ftp.cwd(pathMaster)

	try:
	    file = open(path + photoName,'rb')
	except OSError:
	    print('couldnt open file')
	ftp.storbinary('STOR ' + pathMaster + photoName, file)
	file.close()
	ftp.quit()


        
        
		
# Create an MQTT client and attach our routines to it.
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_SERVER, 1883)

# Process network traffic and dispatch callbacks. This will also handle
# reconnecting.
client.loop_forever()
