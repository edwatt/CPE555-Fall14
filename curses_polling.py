import curses
import time
from gopigo import *

def main(stdscr):
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
if __name__ == '__main__':
    curses.wrapper(main)
