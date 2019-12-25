import paho.mqtt.client as mqtt
from picamera import PiCamera
from time import sleep
import socket
import datetime
from ftplib import FTP

MQTT_SERVER = "192.168.1.103"
#MQTT_SERVER = "test.mosquitto.org"
#MQTT_SERVER = "172.30.21.100"
MQTT_PATH = "test"

camera = PiCamera()

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
	print("Connected with result code "+str(rc))

    # Subscribing in on_connect() - if we lose the connection and
    # reconnect then subscriptions will be renewed.
	client.subscribe(MQTT_PATH)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
	print(msg.topic+" "+str(msg.payload))

#	if msg.payload == "Hello":
	if msg.payload == "Motion Detected":
		print("Received message:" + msg.payload)
		#print(datetime.datetime.now())
		camera.resolution=(3280,2464)
		#camera.framerate =15
		camera.start_preview()
		#sleep(5)
		date = datetime.datetime.now().strftime("%m_%d_%Y_%H_%M_%S_%f")
		#camera.capture('/home/pi/Desktop/' + date + '.jpg')
		filename = date + '_camera2.jpg'
		#camera.capture('/home/pi/Desktop/cameraTrapPhotos/' + date +  '_camera2.jpg')
		path = '/home/pi/Desktop/cameraTrapPhotos/'
		camera.capture(path+filename)
		#camera.capture('/home/pi/Desktop/cameraTrapPhotos/' + filename)
		#camera.capture('/home/pi/Desktop/test.jpg')
		#camera.annotate_text_size = 50
		#camera.annotate_text = date
		camera.stop_preview()
		#print(datetime.datetime.now())
		ftp = FTP(MQTT_SERVER)
		print(ftp.getwelcome())
		login_response = ftp.login('pi','raspberry')
		print(login_response)
		ftp.cwd('Desktop/cameraTrapPhotos')
		print(path+filename)
		try:
			file = open(path+filename,'rb')
			#file = open('/home/pi/Desktop/test.jpg','rb')
		except OSError:
			print('couldnt open file')
		#ftp.storbinary('STOR '+ path+'test.jpg',file)
		ftp.storbinary('STOR ' + path+filename, file)
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
