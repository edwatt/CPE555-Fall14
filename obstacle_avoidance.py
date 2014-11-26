from gopigo import *
import sys

import RPi.GPIO as GPIO

set_speed(150)
turn_time = 0.50 #seconds to turn before reading distance sensor again
GPIO.setmode(GPIO.BCM)
# Initializing pins
TRIG=23
ECHO=24

def main():

	count = 0
	turn = 0 
	timer = 0
	print "Initializing..."

	GPIO.setup(TRIG,GPIO.OUT)
	GPIO.setup(ECHO,GPIO.IN)

	#Setting trigger pin to False to give the sensor time to settle before loop
	GPIO.output(TRIG, False)
	print "Waiting for sensor"
	time.sleep(2)

	#Continually loop, pulsing the sensor every quarter second.  I'm not sure what kind of performance to expect.
	while True:
		
		if timer > 100:
			turn = 0
			timer = 0
		
		if count > 2:
			turn = turn % 1
			count = 0
			
		time.sleep(0.25)
		
		distance = range_sensor_get_dist() # return distance in cm
		
		print distance, " cm"
		
		while distance < 30 and turn == 0:
			print "Turn right"
			count = count + 1
			stop()
			right_rot()
			time.sleep(turn_time)
			stop()
			distance = range_sensor_get_dist()

		while distance < 30 and turn == 1:
			print "Turn left"
			count = count + 1
			stop()
			left_rot()
			time.sleep(turn_time)
			stop()
			distance = range_sensor_get_dist()
		else:
			print "go straight"
		
		fwd();	
		timer = timer + 1
		
		
	GPIO.cleanup()



def range_sensor_get_dist():
	 # The block below sets the Trigger to begin the sensor's routine
        GPIO.output(TRIG, True)
        time.sleep(0.00001)
        GPIO.output(TRIG, False)

        #These while blocks measure the beginning and end times for the distance calculation
        while GPIO.input(ECHO)==0:
                pulse_start = time.time()

        while GPIO.input(ECHO)==1:
                pulse_end = time.time()

        #Here the actual distance is calculated
        duration = pulse_end - pulse_start
        distance = duration * 17150
        distance = round(distance , 2)
	return distance

try:
	main()
except:
	stop()
	GPIO.cleanup()
