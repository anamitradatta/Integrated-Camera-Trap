import paho.mqtt.client as mqtt
from picamera import PiCamera
from time import sleep
import socket
import datetime

MQTT_SERVER = "192.168.0.100"
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
		print("Received message", msg.payload)
		#print(datetime.datetime.now())
		camera.resolution=(2592,1944)
		#camera.framerate =15
		camera.start_preview()
		#sleep(5)
		date = datetime.datetime.now().strftime("%m_%d_%Y_%H_%M_%S_%f")
		#camera.capture('/home/pi/Desktop/' + date + '.jpg')
		camera.capture('/home/pi/Desktop/cameraTrapPhotos/' + date + '.jpg')
		#camera.capture('/home/pi/Desktop/test.jpg')
		#camera.annotate_text_size = 50
		#camera.annotate_text = date
		camera.stop_preview()
		print(datetime.datetime.now())
# Create an MQTT client and attach our routines to it.
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_SERVER, 1883)

# Process network traffic and dispatch callbacks. This will also handle
# reconnecting. Check the documentation at
# https://github.com/eclipse/paho.mqtt.python
# for information on how to use other loop*() functions
client.loop_forever()
