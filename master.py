#!/usr/bin/env python

import curses
import RPi.GPIO as GPIO
import time
from gopigo import *

GPIO.setmode(GPIO.BCM)
# Initializing pins
TRIG=23
ECHO=24

fwd_threshold = 70
bwd_threshold = 30

obstacle_threshold = 35

turn_time = 0.50 #seconds to turn before reading distance sensor again (obstacle avoidance)

# speeds
speed_k = 255
speed_r = 150
speed_a = 255
speed_a_turn = 85 

char_obstacle_avoidance = 'A'
char_range_keeping = 'R'
char_keyboard_control = 'K'
char_quit = 'Q'

char_switches = [ord(char_obstacle_avoidance), ord(char_range_keeping), ord(char_keyboard_control), ord(char_quit)]


def main(stdscr):
	stdscr.move(0, 0)
	stdscr.addstr("Raspi Robot Control")
	stdscr.move(1, 0)
	stdscr.addstr("Use one of the following keys to select your mode. You can change modes at any time.")
	stdscr.move(2, 0)
	stdscr.addstr("A - Obstacle Avoidance")
	stdscr.move(3, 0)
	stdscr.addstr("R - Range Keeping")
	stdscr.move(4, 0)
	stdscr.addstr("K - Keyboard Control")
	stdscr.move(5, 0)
	stdscr.addstr("Q - Quit")
	stdscr.move(6,0)
	stdscr.addstr("Current Mode: ")

	try:
		mode = None

		while True:
			try:
				stdscr.nodelay(1)

				if mode == 'K':
					keyboard_control(stdscr)
				elif mode == "R":
					range_keep(stdscr)
				elif mode == "A":
					obstacle_avoidance(stdscr)
				else:
					c = poll_screen(stdscr)
					stdscr.move(7,0)
					stdscr.clrtoeol()
					stdscr.addstr(str(c))
			except SwitchMode as e:
				stop()
				if e.value == 'Q':
					raise
				else:
					mode = e.value
					stdscr.move(6,0)
					stdscr.addstr("Current Mode: " + mode)

	except SwitchMode as e:
		pass # catching Q to quit program
	finally:
		stop()
		GPIO.cleanup()
		

def keyboard_control(stdscr):
	# do not wait for input when calling getch
	stdscr.nodelay(1)
	stdscr.move(7, 0)
	
	set_speed(speed_k)	
	key_pressed = -1

	while True:
		# get keyboard input, returns -1 if none available
		c = poll_screen(stdscr)
		if c != -1 and c != key_pressed:
			curses.flushinp()
			time.sleep(0.15)
			c = poll_screen(stdscr)

			stdscr.addstr(str(c))
			stdscr.refresh()
			stdscr.move(7, 0)
			key_pressed = c

			stop()
			
			if c == curses.KEY_UP:
				motor_fwd()
			elif c == curses.KEY_DOWN:
				motor_bwd()
			elif c == curses.KEY_LEFT:
				left_rot()
			elif c == curses.KEY_RIGHT:
				right_rot()

		elif c == -1:
			stdscr.move(7, 0)
			stdscr.clrtoeol()
			stdscr.addstr("STOP")
			stdscr.refresh()
			stdscr.move(7, 0)

			if key_pressed != -1:
				stop()
				key_pressed = -1

		time.sleep(0.15)
		curses.flushinp() 
		time.sleep(0.15)


def range_keep(stdscr):
	set_speed(speed_r)
	stdscr.nodelay(1)

	#print "Initializing..."

	GPIO.setup(TRIG,GPIO.OUT)
	GPIO.setup(ECHO,GPIO.IN)

	#Setting trigger pin to False to give the sensor time to settle before loop
	GPIO.output(TRIG, False)
	#print "Waiting for sensor"
	time.sleep(2)

	#Continually loop, pulsing the sensor every quarter second.  I'm not sure what kind of performance to expect.
	while True:

		poll_screen(stdscr)
		time.sleep(0.25)
	
		distance = range_sensor_get_dist()
		#print distance, " cm"
		
		#If the distance is greater than 90 cm the robot should move forward.
		#If the distance is less than 45 cm it should move back.
		#Otherwise it should stand still.
		#Print commands are filler for now.
		if distance > fwd_threshold:
			#print "Going Forward"
			motor_fwd()
		elif distance < bwd_threshold:
			#print "Going Backward"
			motor_bwd()
		else:
			#print "Standing Still"
			stop()

def obstacle_avoidance(stdscr):

	set_speed(speed_a)
	stdscr.nodelay(1)

	count = 0
	turn = True
	timer = 0
	#print "Initializing..."

	GPIO.setup(TRIG,GPIO.OUT)
	GPIO.setup(ECHO,GPIO.IN)

	#Setting trigger pin to False to give the sensor time to settle before loop
	GPIO.output(TRIG, False)
	#print "Waiting for sensor"
	time.sleep(2)

	#Continually loop, pulsing the sensor every quarter second.  I'm not sure what kind of performance to expect.
	while True:
		
		if timer > 100:
			turn = True
			timer = 0
		
		if count > 2:
			turn = not turn
			count = 0
			
		time.sleep(0.25)
		poll_screen(stdscr)
		
		distance = range_sensor_get_dist() # return distance in cm
		
		# print distance, " cm"
	
		#stdscr.move(10,0)
		#stdscr.addstr("Count: " + str(count))
		#stdscr.move(11,0)
		#stdscr.addstr("Turn: " + str(turn))
		
		while distance < obstacle_threshold and turn:
			#print "Turn right"
			count = count + 1
			stop()
			set_speed(speed_a_turn)
			right_rot()
			time.sleep(turn_time)
			stop()
			time.sleep(0.25)
			distance = range_sensor_get_dist()
			time.sleep(0.10)

		while distance < obstacle_threshold and not turn:
			#print "Turn left"
			count = count + 1
			stop()
			set_speed(speed_a_turn)
			left_rot()
			time.sleep(turn_time * 1.5)
			stop()
			time.sleep(0.25)
			distance = range_sensor_get_dist()
			time.sleep(0.10)
		
		set_speed(speed_a)
		motor_fwd();	
		timer = timer + 1



def range_sensor_get_dist():

    pulse_start = None
    pulse_end = None
    # The block below sets the Trigger to begin the sensor's routine
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    #These while blocks measure the beginning and end times for the distance calculation
    while GPIO.input(ECHO)==0:
            pulse_start = time.time()

    while GPIO.input(ECHO)==1:
            pulse_end = time.time()

    if pulse_start and pulse_end:
	    #Here the actual distance is calculated
	    duration = pulse_end - pulse_start
	    distance = duration * 17150
	    distance = round(distance , 2)
	    return distance
    else:
    	return range_sensor_get_dist()




def poll_screen(stdscr):
	c = stdscr.getch()

	if c in char_switches or (c - 32) in char_switches:
		raise SwitchMode(chr(c).upper()) # throw exception
	else:
		return c


class SwitchMode(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)


if __name__ == '__main__':
	curses.wrapper(main)
