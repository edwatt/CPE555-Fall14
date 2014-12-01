#!/usr/bin/env python

import curses
import RPi.GPIO as GPIO
import time
from gopigo import *

GPIO.setmode(GPIO.BCM)
# Initializing pins
TRIG=23
ECHO=24

fwd_threshold = 40
bwd_threshold = 20

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
		# catching Q to quit program
		stop()
		GPIO.cleanup()

def keyboard_control(stdscr):
	# do not wait for input when calling getch
	stdscr.nodelay(1)
	stdscr.move(7, 0)
	
	set_speed(255)	
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
				fwd()
			elif c == curses.KEY_DOWN:
				bwd()
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


def range_keep():

	stdscr.nodelay(1)
	poll_screen(stdscr)

	#print "Initializing..."

	GPIO.setup(TRIG,GPIO.OUT)
	GPIO.setup(ECHO,GPIO.IN)

	#Setting trigger pin to False to give the sensor time to settle before loop
	GPIO.output(TRIG, False)
	#print "Waiting for sensor"
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
		#print distance, " cm"
		
		#If the distance is greater than 90 cm the robot should move forward.
		#If the distance is less than 45 cm it should move back.
		#Otherwise it should stand still.
		#Print commands are filler for now.
		if distance > fwd_threshold:
			#print "Going Forward"
			fwd()
		elif distance < bwd_threshold:
			#print "Going Backward"
			bwd()
		else:
			#print "Standing Still"
			stop()




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