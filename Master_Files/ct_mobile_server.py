#!/usr/bin/env python3

import socket
import os
import subprocess
from time import sleep
from ftplib import FTP
#import paramiko

#AUTHORS: 
#Anamitra Datta
#Max Haimowitz 

#mobile app source code written by Max Haimowitz

#Mobile App server code. Download the mobile app code from the ITC github page and install it on your android phone. 
#This app listens to messages sent by the Camera Trap app and performs commands, outputs text, and sends notifications to the phone's app
#Commands: download Photos, start the system, stop the system, etc.
#Install this code on the master Pi only
#First run this mobile server code, then run the app. Connect to the IP address of the master Pi and the port number (default: 8888)

#Run an FTP server app on the mobile phone. Make sure you configure the correct port, password, and username for the FTP server
#Also make sure you are connected to the correct network
#FTP Server App:
#https://play.google.com/store/apps/details?id=com.medhaapps.wififtpserver&hl=en_US

def check_ftp(server_ip, port):
    try:
        test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        test_socket.connect((server_ip, port))
    except Exception:
        # not up, log reason from ex if wanted
        return False
    else:
        test_socket.close()
    return True

HOST = '192.168.5.101' #IP Address of the Master Pi
PORT = 8888 # Port to listen on (non-privileged ports are > 1023)

CLIENT = ' ' #Client IP address for phone, will detect this automatically, no need to fill in
#MAKE SURE PHONE IS CONNECTED TO CORRECT WIFI NETWORK
CLIENT_PORT = 2221 #Client port for FTP server on phone
#MAKE SURE FTP SERVER IS RUNNING ON PHONE AND USES THE SAME PORT

print ('Starting up Camera Trap Mobile Server')
path = "/home/pi/cameraTrapPhotos/" #directory for photos

#networking code to start and listen for incoming connections
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s: #connect to WiFi connection
    s.bind((HOST, PORT)) #Use port for host for mobile server
    while True:
        s.listen() #listen for incoming connections
        conn, addr = s.accept() #when it gets a connection (from the phone), it will accept it
        with conn:
            CLIENT = addr[0] #set Client IP address
            print('Connected by', CLIENT)
            while True:
                data = conn.recv(1024) # message from phone
                if not data: #if no data is received, then break the connection
                    break

                MESSAGE = data.decode().strip(); #decode the message

                #You must put NOTIFICATION before send a message to the phone in order for the phone to print the message on the app
                #see examples below

                #Test Sending Picture
                if "picture" == MESSAGE:
                    print("Sending Picture...")
                    conn.sendall(b'NOTIFICATION: Sending Picture...\n') #send notification to phone that picture is being sent
                    ftp = FTP() #open FTP server
                    ftp.connect(CLIENT,CLIENT_PORT) #connect to FTP server on phone
                    ftp.login('android','android') #username and password for FTP Client, change if needed
                    ftp.cwd('Download') #change to SDCard directory
                    file = open('/home/pi/test_photo.jpg','rb')
                    ftp.storbinary('STOR ' + '/Download/test_photo.jpg', file)
                    file.close()
                    ftp.quit()
                    print ("Picture Sent to Phone")
                    conn.sendall(b'NOTIFICATION: Picture Sent to Phone\n') #send notification to phone that photo has been sent

                #Was used for power checking from SDP20, now not needed, can be removed
                elif "powerCheck" == MESSAGE:
                    conn.sendall(b'NOTIFICATION: Power Checking Stuff...')
                    print("Power Checking Stuff...")

                #rename to ftpCheck
                #Check if FTP port is open
                elif ("sshCheck" == MESSAGE or "ftpCheck"==MESSAGE):
                    print("Checking FTP into phone...")
                    if check_ftp(CLIENT, CLIENT_PORT)==True:
                        print("RPi can ftp into phone")
                        conn.sendall(b'NOTIFICATION: RPi can ftp into phone\n')
                    else:
                        print("RPi cannot ftp into phone")
                        conn.sendall(b'NOTIFICATION: RPi cannot ftp into phone\n')

                #Test stubs, can be removed, were used for debugging and testing
                elif "checkConnection" == MESSAGE:
                    print("Checking Connection")

                elif "testMessage" == MESSAGE:
                    conn.sendall(b'NOTIFICATION: Sample Message Received...\n')
                    print("Testing Message...")

                #Checks if camera is connected to the Pi correctly
                elif "checkCamera" == MESSAGE:
                    print("Checking Camera...")
                    #this command checks whether the camera is supported and detected
                    cameraConnCheck = subprocess.check_output("vcgencmd get_camera", shell=True);
                    expected_output = u'supported=1 detected=1\n' #this should be the output if camera is supported and detected
                    actual_output = cameraConnCheck.decode()
                    #print("Expected: "+ expected_output)
                    #print("Actual: " + actual_output)
                    if(cameraConnCheck.decode() in expected_output): #if the output is correct, camera is connected
                        print("camera is supported and detected")
                        conn.sendall(b'NOTIFICATION: Camera is supported and detected\n')
                    else:
                        print("camera is not supported and detected")
                        conn.sendall(b'NOTIFICATION: Camera is not supported and detected\n')

                #SSH Paramiko library: http://docs.paramiko.org/en/stable/api/client.html

                #NEEDS TO BE IMPROVED to start slaves (via services) as well through SSH using Paramiko library
                #RENAME STARTMASTER TO STARTSYSTEM
                #can choose to use one sensor program or multiple sensor program
                elif ("startSystem" == MESSAGE or "startMaster"==MESSAGE): #if message is start master, start the CT program
                    print("Starting System...")
                    conn.sendall(b'NOTIFICATION: Starting system...\n') #send notification to phone that system has started
                    #start master program in background
                    #THIS SHOULD BE CHANGED TO A SERVICE
                    cmdStartMaster = "python -u /home/pi/ct_publish_master.py > /home/pi/ct_output.txt 2>/home/pi/ct_error.txt </dev/null &" 
                    os.system(cmdStartMaster) #start master CT program
                    #now we need to start program on all slave Pis through ssh and perform ssh command for starting service

                #NEEDS TO BE IMPLEMENTED to stop master CT program and also CT slave programs through Paramiko SSH
                #This should stop the CT Program Service on Master and slave devices
                elif("stopSystem" == MESSAGE or "stopMaster"==MESSAGE):
                    print("stopping System...")
                    conn.sendall(b'NOTIFICATION: Stopping System...\n') #send notification to phone that system has stopped
                    #need to stop program on master Pi possibly using service command by getting PID and using killing process command
                    #need to stop program on slave pis by ssh and running ssh command to stopping service

                #delete photos from master and slave devices
                #NEEDS TO BE IMPROVED to delete photos from all slave devices as well through SSH Paramiko
                #ADD BUTTON FOR THIS in mobile app code
                elif ("deletePhotos" == MESSAGE):
                    print("Deleting photos...")
                    conn.sendall(b'NOTIFICATION: Deleting photos from Master\n')
                    delPhotosCmd = 'sudo rm -r /home/pi/cameraTrapPhotos/*'
                    os.system(delPhotosCmd)
                    #SSH into all slave Pis and run command to delete photos from their own CameraTrapPhotos directories

                #RENAME MOVEPICTURES TO DOWNLOADPICTURES
                elif ("downloadPictures" == MESSAGE or "movePictures"==MESSAGE): #if message is move pictures, FTP pictures to phone
                    #MAKE SURE FTP SERVER APP IS RUNNING ON THE PHONE
                    ftp = FTP()
                    ftp.connect(CLIENT,CLIENT_PORT) #connect to FTP server on phone
                    ftp.login('android','android') #username and password for FTP Client, change if needed
                    ftp.cwd('Download')
                    numPhotos = 0

                    #get number of photos
                    for root, dirs, files in os.walk(path):
                        for dname in dirs:
                            for sroot, sdirs, photos in os.walk(path+dname):
                                for photo in photos:
                                    numPhotos += 1

                    #FTP Photos to phone
                    print("sending photos")
                    conn.sendall(b'NOTIFICATION: sending photos\n')
                    currentPhoto = 0
                    for root, dirs, files in os.walk(path):
                        for dname in dirs:
                            ftp.mkd(dname)
                            ftp.cwd(dname)
                            for sroot, sdirs, photos in os.walk(path+dname):
                                for photo in photos:
                                    currentPhoto += 1
                                    print("sending photo number " + str(currentPhoto) + " out of " + str(numPhotos))
                                    try:
                                        file = open(path+dname+'/'+photo,'rb')
                                    except OSError:
                                        print("could not open file")

                                    ftp.storbinary('STOR ' + '/Download/'+dname+'/' + photo, file)

                                    print("sent photo number " + str(currentPhoto) + "out of " + str(numPhotos) + " to phone")
                                    file.close()
                            ftp.cwd('..')
                    ftp.quit()
                    #End FTP Session

                    print("done. sent all photos to phone")
                    conn.sendall(b'NOTIFICATION: sent all photos\n')

                else:
                    print ('Received Message from Phone')
                    conn.sendall(b'MESSAGE: ' + data)
