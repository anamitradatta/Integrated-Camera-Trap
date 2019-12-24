import paho.mqtt.publish as publish
from picamera import PiCamera
from time import sleep
from gpiozero import MotionSensor
import socket
import datetime
import os, shutil
from ftplib import FTP

MQTT_SERVER = "localhost"
MQTT_PATH = "test"

camera = PiCamera()
pir = MotionSensor(4)

#Default Variables
resolutionHeight = 3280
resolutionWidth = 2464

modeInput = raw_input("Enter Camera Exposure Mode (Auto, Sport, or Manual): ")

delayInput = 0.4

if modeInput == "Auto":
    print("\nAutomatic Mode Selected\n")
if modeInput == "Sport":
    print("\nSport Mode Selected (Fast shutter)\n")
elif modeInput == "Manual":
    print("\nManual Mode Selected\n")
    sleep(1)
    delayInput = input ("Enter Delay in Secs : ")
    shutterInput = input ("Shutter Speed milliSecs: ")
    brightnessInput = input ("Brightness (1 - 100): ")
    sleep(1)
    print "\n\nCamera Stats..."
    print "Camera Resolution: ",resolutionHeight,"x",resolutionWidth
    print "Special Exposure Mode Not Selected"
    print "Time Between Detection and Capture: ", delayInput
    print "Shutter Speed Selected (microseconds): ", shutterInput*1000
    print "Brightness Selected: ", brightnessInput
else:
    shutterInput = 4
    brightnessInput = 60
    print(modeInput)


sleep(1)
startInput = raw_input ("\nStart Code? (y/n): ")
sleep(1)
print('\nStarting Master Code...\n')

if (os.path.isdir('/home/pi/Desktop/walkTestPhotos')):
    shutil.rmtree('/home/pi/Desktop/walkTestPhotos')
    os.mkdir('/home/pi/Desktop/walkTestPhotos')

sleep(1)

photoNum = 1

while startInput == "y":
    print('\nSensor Cool Down (10 seconds)')
    for i in reversed(xrange(9)):
        print i+1, "seconds"
        sleep(1)
    print('\nDone Resting \n\n')
    
    camera.resolution = (resolutionHeight, resolutionWidth) #8 MegaPixels
    camera.shutter_speed = shutterInput*1000 #4ms shutter speed
    camera.brightness = brightnessInput #enhanced brightness
    
    if (modeInput == "Auto"):
        camera.exposure_mode = 'auto' #auto exposure mode
    if (modeInput == "Sport"):
        camera.exposure_mode = 'sports' #sports exposure mode, automatic fast shutter
    if (modeInput == "Manual"):
        camera.shutter_speed = shutterInput*1000 #4ms shutter speed
        camera.brightness = brightnessInput #enhanced brightness
    
    pir.wait_for_no_motion()
    print('Waiting for Motion...\n')
    
    
    #Here we transmit out a signal
    pir.wait_for_motion()
    
    print('Motion Detected!\n\n')
        
    message = "Motion Detected"
    message += " - PhotoNum: " + str(photoNum)
    message += " Delay: " + str(delayInput)
    message += " ShutterSpeed: " + str(shutterInput)
    message += " Brightness: " + str(brightnessInput)
    
    #Send out message to Take Photo
    publish.single(MQTT_PATH, message, hostname=MQTT_SERVER)
    
    word_list = message.split()
    brightnessInput = int(word_list[-1])
    shutterInput = int(word_list[-3])
    delayInput = float(word_list[-5])
    photoNum = int(word_list[-7])
    camera.exposure_mode = 'sports'
    
    if (word_list[0] == "Motion"):
        
        path = '/home/pi/Desktop/'
        fileName = 'walkTest_cam1_photo' + str(photoNum) + '.jpg'
        camera.resolution = (resolutionHeight, resolutionWidth) #8 MegaPixels
        camera.shutter_speed = shutterInput*1000 #4ms shutter speed
        camera.brightness = brightnessInput #enhanced brightness

        camera.start_preview()
        sleep(delayInput) #warm up camera
        firstLocation = path + fileName
        camera.capture(firstLocation)
        camera.stop_preview()
        
        
    
        #Moving Photos
        newFileName = path
        newLocation = path + '/walkTestPhotos/' + fileName
        print "Captured Photo Number", photoNum
    
        shutil.move(firstLocation, newLocation)
        #MQTT Publish to walkTest
        #FTP Walktest Stuff

        photoNum+=1
    
