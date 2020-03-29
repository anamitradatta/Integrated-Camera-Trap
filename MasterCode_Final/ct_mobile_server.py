#!/usr/bin/env python3

import socket
import os
import subprocess
from time import sleep
from ftplib import FTP

HOST = '192.168.5.101' #IP Address of the Master Pi
PORT = 8888 # Port to listen on (non-privileged ports are > 1023)

CLIENT = ' ' #Client IP address for phone, will detect this automatically, no need to fill in
#MAKE SURE PHONE IS CONNECTED TO CORRECT WIFI NETWORK
CLIENT_PORT = 2221 #Client port for FTP server on phone
#MAKE SURE FTP CLIENT IS RUNNING ON PHONE AND USES THE SAME PORT

print ('Starting up mobile server')
path = "/home/pi/cameraTrapPhotos/" #directory for photos

#networking code to start and listen for incoming connections
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s: #connect to WiFi connection
    s.bind((HOST, PORT)) #Use port for host for mobile server
    while True:
        s.listen() #listen for incoming connections
        conn, addr = s.accept() #when it gets a connection (from the phone), it will accept it
        with conn:
            CLIENT = addr[0] #Client IP address
            print('Connected by', CLIENT)
            while True:
                data = conn.recv(1024) # message from phone
                if not data:
                    break

                MESSAGE = data.decode().strip();
                
                #NEEDS TO BE IMPROVED to start slaves (services) as well through SSH using Paramiko library : http://docs.paramiko.org/en/stable/api/client.html
                elif ("startMaster" == MESSAGE): #if message is start master, start the CT program
                    print("Starting Master...")
                    conn.sendall(b'NOTIFICATION: Starting Master...\n') #send notification to phone to start master
                    #start master program in background
                    #THIS SHOULD BE CHANGED TO A SERVICE
                    cmdStartMaster = "python -u /home/pi/ct_publish_master.py > /home/pi/ct_output.txt 2>/home/pi/ct_error.txt </dev/null &" 
                    
                    os.system(cmdStartMaster) #start master CT program

                elif "movePictures" == MESSAGE: #if message is move pictures, FTP pictures to phone
                    #MAKE SURE FTP CLIENT IS RUNNING ON THE PHONE
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
