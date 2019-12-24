import sys
import os
import time

usb_bool = False
led_bool = False
hdmi_bool = False
bluetooth_bool = False

usb_delay = 0
led_delay = 0
hdmi_delay = 0
bluetooth_delay = 0

if ("usb" in str(sys.argv)):
    usb_delay = int( sys.argv[(sys.argv).index("usb") + 1])
    usb_bool = True
    
if ("led" in str(sys.argv)):
    led_delay = int(sys.argv[(sys.argv).index("led") + 1])
    led_bool = True
    
if ("hdmi" in str(sys.argv)):
    hdmi_delay = int(sys.argv[(sys.argv).index("hdmi") + 1])
    hdmi_bool = True

if ("bluetooth" in str(sys.argv)):
    bluetooth_delay = int(sys.argv[(sys.argv).index("bluetooth") + 1])
    bluetooth_bool = True

if usb_bool:
    print "turning off usb for ",usb_delay," seconds"
    os.system("sudo sh -c \"echo 0 > /sys/devices/platform/soc/3f980000.usb/buspower\"")

if led_bool:
    print "turning off led for ",led_delay," seconds"
    os.system("sudo sh -c \"echo 0 > /sys/class/leds/led1/brightness\"")

if hdmi_bool:
    print "turning off hdmi for ",hdmi_delay," seconds"
    os.system("/usr/bin/tvservice -o")

if bluetooth_bool:
    print "turning off bluetooth for ",bluetooth_delay," seconds"
    os.system("sudo rfkill block bluetooth")
    
if not usb_bool and not led_bool and not hdmi_bool and not bluetooth_bool:
    print "Nothing selected to turn off!"

count = 0
while (usb_bool or led_bool or hdmi_bool or bluetooth_bool):
    if (count >= usb_delay and usb_bool == True):
        os.system("sudo sh -c \"echo 1 > /sys/devices/platform/soc/3f980000.usb/buspower\"")
        print("turning usb back on")
        usb_bool = False
    if (count >= led_delay and led_bool == True):
        print ("turning led back on")
        os.system("sudo sh -c \"echo 1 > /sys/class/leds/led1/brightness\"")
        led_bool = False
    if (count >= hdmi_delay and hdmi_bool == True):
        os.system("/usr/bin/tvservice -p")
        print ("turning hdmi back on")
        hdmi_bool = False
    if (count >= bluetooth_delay and bluetooth_bool == True):
        print ("turning bluetooth bac on")
        os.system("sudo rfkill unblock bluetooth")
        bluetooth_bool = False
    

    time.sleep(1)
    count +=1

    
