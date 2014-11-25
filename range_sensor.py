import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BCM)
# Initializing pins
TRIG=23
ECHO=24

print "Initializing..."

GPIO.setup(TRIG,GPIO.OUT)
GPIO.setup(ECHO,GPIO.IN)

#Setting trigger pin to False to give the sensor time to settle before loop
GPIO.output(TRIG, False)
print "Waiting for sensor"
time.sleep(2)

#Continually loop, pulsing the sensor every quarter second.  I'm not sure what kind of performance to expect.
while True:
	time.sleep(0.25)
	
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
	print distance, " cm"
	
	#If the distance is greater than 90 cm the robot should move forward.
	#If the distance is less than 45 cm it should move back.
	#Otherwise it should stand still.
	#Print commands are filler for now.
	if distance > 90:
		print "Going Forward"
	elif distance < 45:
		print "Going Backward"
	else:
		print "Standing Still"
	
	
GPIO.cleanup()
