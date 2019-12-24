# MQTT Publish Demo
# Publish two messages, to two different topics

import paho.mqtt.publish as publish
from picamera import PiCamera
from time import sleep
from gpiozero import MotionSensor
import socket
import datetime

#MQTT_SERVER = "192.168.0.19"
#MQTT_SERVER = "test.mosquitto.org"
MQTT_SERVER = "localhost"
MQTT_PATH = "test"
camera = PiCamera()
pir = MotionSensor(4)

#_______________________Socket Connection______________________________
s = socket.socket()
port = 1234

s.bind(('',port))
s.listen(10)
c,addr = s.accept()
#c.settimeout(5)
print('socket connected')
#______________________________________________________
client_message = "Motion Not Detected"
message = "Motion Not Detected"
#index = 0
while True:
    #client_message = "Motion Not Detected"
    #message = "Motion Not Detected"
    #goon =0
	#print("Sensor resting")
    sleep(2)
    publish.single(MQTT_PATH, message, hostname=MQTT_SERVER)
    sleep(10)
    print("Done sleeping")
    #publish.single(MQTT_PATH, message, hostname=MQTT_SERVER)
    n = 0
    while True:
	sleep(1)
	client_message = c.recv(1)
	print(client_message)

	if client_message == "T":
            n = 1
        else:
            n = 0
    
	if n == 0:
            print("zero sensor active")
            
        if n == 1:
            print("one sensor active")
	
        if pir.motion_detected == False or n == 0:
            message = "again"
            publish.single(MQTT_PATH, message, hostname=MQTT_SERVER)
            print("a")
        elif pir.motion_detected == True and n == 1:
            message = "Motion Detected"
            #print("Motion has been detected")
            print("two sensors active")
            print("Take pictures")
            
            publish.single(MQTT_PATH, message, hostname=MQTT_SERVER)
            message = "Motion Not Detected"
            print("Sent message: ", message)
            camera.resolution=(3280,2464)
            camera.exposure_mode = 'sports'
#        camera.shutter_speed = 4000;
#        camera.brightness= 60
            camera.start_preview()
#   sleep(2)
            date = datetime.datetime.now().strftime("%m_%d_%Y_%H_%M_%S_%f")
            filename = date+ '_camera1.jpg'
    #camera.capture('/home/pi/Desktop/' + date + '.jpg')
            path = '/home/pi/Desktop/cameraTrapPhotos/'
    #camera.capture('/home/pi/Desktop/cameraTrapPhotos/' + date + "_camera1" + '.jpg')
            camera.capture(path+filename)
    #camera.capture('/home/pi/Desktop/test.jpg')
            camera.stop_preview()
            print(datetime.datetime.now())
            #publish.single(MQTT_PATH, message, hostname=MQTT_SERVER)
            break

'''
        else:
            #message = "F"
            print("one sensor active")
            #print("Motion NOT detected")
            #publish.single(MQTT_PATH, message, hostname=MQTT_SERVER)
            continue
'''        
    
               

		#index+=1
        
        