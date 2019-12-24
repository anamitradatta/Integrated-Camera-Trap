from time import sleep
import RPi.GPIO as GPIO
from picamera import PiCamera
import paho.mqtt.publish as publish
import os
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

camera = PiCamera()
MQTT_SERVER = "localhost"
MQTT_PATH = "test"

if (os.path.isdir('/home/pi/Desktop/cameraTrapPhotos') == False):
    print "Make Sure there is a cameraTrapPhotos Folder"

os.system("sudo rm ../cameraTrapPhotos/*")

Matrix = [ [1,2,3,'A'],
	    [4,5,6,'B'],
	    [7,8,9,'C'],
	    ['*',0,'#','D'] ]

display = [ [1,1,1,1,1,1,0],
            [1,1,0,0,0,0,0],
            [0,1,1,0,1,1,1],
            [1,1,1,0,0,1,1],
            [1,1,0,1,0,0,1],
            [1,0,1,1,0,1,1],
            [1,0,1,1,1,1,1],
            [1,1,1,0,0,0,0],
            [1,1,1,1,1,1,1],
            [1,1,1,1,0,1,1] ]

value = -1

ROW = [32,36,38,40]
COL = [31,33,35,37]

DIGIT= [18,22]
Segments = [11,13,15,19,21,23,29]
GOON = 0;

photoNum = 1
photoNum_cam2 = 1
photoNum_cam3 = 1

for k in range(2):
	GPIO.setup(DIGIT[k],GPIO.OUT)
        GPIO.output(DIGIT[k],1)

for m in range(7):
	GPIO.setup(Segments[m],GPIO.OUT)
	GPIO.output(Segments[m],1)
	
for j in range(4):
	GPIO.setup(COL[j],GPIO.OUT)
	GPIO.output(COL[j],1)

for i in range(4):
	GPIO.setup(ROW[i],GPIO.IN,pull_up_down = GPIO.PUD_UP)


try:
	while(GOON ==0):
		for j in range(4):
			GPIO.output(COL[j],0)
			#print("a")
			for i in range(4):
				if GPIO.input(ROW[i]) == 0:
					print Matrix[i][j]
					camNumber = Matrix[i][j]

					if type(Matrix[i][j]) != str and value < 0: 
                                              value = Matrix[i][j]                                                   
                                           
                                        elif type(Matrix[i][j]) != str and value >0:
                                              value = value*10+Matrix[i][j]
                                        
                                        # new code
                                        
                                        if Matrix[i][j] == 'C':
                                            value = -1
                                            for I in range(7):
                                               GPIO.output(Segments[I],0)
                                            
                                            GPIO.output(DIGIT[0],1)  
                                            GPIO.output(DIGIT[1],1)  
                                        
                                        elif Matrix[i][j] == '#':
                                            print("set")
                                            GOON =-1
                                            break
                                        
					if(camNumber ==1):
						#take photo on this camera
						path = '/home/pi/Desktop/cameraTrapPhotos/'
        					photoName = 'keypad1_' + str(photoNum) + '.jpg'
						camera.resolution = (3240, 2464)
        					camera.shutter_speed = 30000
        					camera.start_preview()
        					sleep(1)
        					camera.capture(path + photoName)
        					camera.stop_preview()
        					print "Photo Number", photoNum, " taken"
        					photoNum += 1
					if(camNumber ==2 or camNumber==3):
						#send mqtt message
                                            
						message= "Cam-Number: " + str(camNumber) + " Photo-Num: "
						
						if (camNumber == 2):
                                                    message += str(photoNum_cam2)
                                                    photoNum_cam2 += 1
                                                if (camNumber == 3):
                                                    message += str(photoNum_cam3)
                                                    photoNum_cam3 += 1
                                                publish.single(MQTT_PATH, message, hostname=MQTT_SERVER)


                                        #print(value)
                                        """
                                        if value >=10:
                                          Udigit = value%10
                                          newvalue = int(value/10)
                                          Tdigit = newvalue%10
                                        else:
                                          Tdigit = -1
                                          Udigit = value
                                            
                                          
                                        
                                        for index in range(10):
                                            
                                            #print(Tdigit)
                                            if Tdigit == index:
                                               GPIO.output(DIGIT[0],0)   
                                               for I in range(7):
                                                 
                                                 if display[index][I] == 0:
                                                 #GPIO.output(DIGIT[0],0)
                                                   GPIO.output(Segments[I],0)
                                                 
                                                 else:
                                                   GPIO.output(Segments[I],1)
                                            
                    
    				   	
                                        
                                        for index in range(10):
                                            
                                            
                                            if Udigit == index:
                                                
                                               GPIO.output(DIGIT[1],0)   
                                               for I in range(7):
                                                 
                                                 if display[index][I] == 0:
                                                 #GPIO.output(DIGIT[0],0)
                                                   GPIO.output(Segments[I],0)
                                                 
                                                 else:
                                                   GPIO.output(Segments[I],1)
                                            
                                        """
                                        
                                        sleep(0.1)
                                                                
					while(GPIO.input(ROW[i]) == 0):
						pass

                                
                                else:
                                        
                                        if value >=10:
                                          Udigit = value%10
                                          newvalue = int(value/10)
                                          Tdigit = newvalue%10
                                        
                                        else:
                                          Tdigit = -1
                                          Udigit = value
                                         
                                        #print(Tdigit)
                                        
                                        """
                                        for index in range(10):
                                            
                                            #print(Tdigit)
                                            if Tdigit == index:
                                               GPIO.output(DIGIT[0],1)   
                                               for I in range(7):
                                                 
                                                 if display[index][I] == 0:
                                                   GPIO.output(DIGIT[0],0)
                                                   GPIO.output(Segments[I],0)
                                                 
                                                 else:
                                                   GPIO.output(Segments[I],1)
                                             
                                               sleep(0.001)
                                               GPIO.output(DIGIT[0],1)  
    				   	   """    
                                        
                                        for index in range(10):
                                            
                                            
                                            if Udigit == index:
                                                
                                               GPIO.output(DIGIT[1],0)   
                                               for I in range(7):
                                                 
                                                 if display[index][I] == 0:
                                                 #GPIO.output(DIGIT[0],0)
                                                   GPIO.output(Segments[I],0)
                                                 
                                                 else:
                                                   GPIO.output(Segments[I],1)
                                                   
                                               sleep(0.001)
                                               GPIO.output(DIGIT[1],1)
                                               
                                
			GPIO.output(COL[j],1)

except KeyboardInterrupt:
	GPIO.cleanup()
	
