import curses
import time
from gopigo import *

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

	mode = None

	while True:
		try:
			c = poll_screen(stdscr)
			stdscr.move(7,0)
			stdscr.addstr(str(c))
		except SwitchMode as e:
			if e.value == 'Q':
				raise
			else:
				mode = e.value
				stdscr.move(6,0)
				stdscr.addstr("Current Mode: " + mode)

def keyboard_control(stdscr):
	# do not wait for input when calling getch
	stdscr.nodelay(1)
	
	set_speed(255)	
	key_pressed = -1

	while True:
		# get keyboard input, returns -1 if none available
		c = stdscr.getch()
		if c != -1 and c != key_pressed:
			curses.flushinp()
			time.sleep(0.15)
			c = stdscr.getch()

			stdscr.addstr(str(c))
			stdscr.refresh()
			stdscr.move(0, 0)
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
			stdscr.clrtoeol()
			stdscr.addstr("STOP")
			stdscr.refresh()
			stdscr.move(0, 0)

			if key_pressed != -1:
				stop()
				key_pressed = -1

		time.sleep(0.15)
		curses.flushinp() 
		time.sleep(0.15)


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