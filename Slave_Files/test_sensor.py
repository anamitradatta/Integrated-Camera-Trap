from time import sleep
from gpiozero import MotionSensor

pir = MotionSensor(4)

while True:
	sleep(1)
	print(pir.motion_detected)