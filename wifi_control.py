import curses
stdscr = curses.initscr()
curses.cbreak()
stdscr.keypad(1)

stdscr.addstr(0,10,"Hit 'q' to quit")
stdscr.refresh()

key = ''
while key != ord('q'):
    key = stdscr.getch()
    stdscr.addch(20,25,key)
    stdscr.refresh()
    if key == curses.KEY_UP: 
        #move forward code
	stdscr.addstr(2, 20, "Up")
    elif key == curses.KEY_DOWN: 
        stdscr.addstr(3, 20, "Down")
    else: 
	stdscr.move(2,20)
	stdscr.clrtobot()

curses.endwin()
