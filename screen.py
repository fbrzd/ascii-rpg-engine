from time import sleep
import threading
import curses

class Screen:
    def __init__(self):

        self.scr = curses.initscr()
        self.max_Y, self.max_X = self.scr.getmaxyx()
        #self.colors = dict() # palette

        curses.start_color() # use colors
        curses.noecho() # no echo
        curses.cbreak() # not buffer
        curses.curs_set(0) # no blink cursor
        #self.scr.nodelay(1) # getch not blocking... check "halfdelay"
        curses.halfdelay(5)
        self.scr.keypad(1) # special keys

        # colors default:
        # 0:black, 1:red, 2:green, 3:yellow, 4:blue, 5:magenta, 6:cyan, and 7:white.
        #curses.init_pair(0, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(6, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(7, curses.COLOR_WHITE, curses.COLOR_BLACK)
        
        #curses.init_pair(pair_index, fcol, curses.COLOR_BLACK)

    def refresh(self):
        #self.scr.border('|','|','-','-','+','+','+','+')
        self.scr.refresh()
    
    def magic_test_function(self):
        #curses.start_color()
        curses.use_default_colors()
        for i in range(0, curses.COLORS):
            curses.init_pair(i + 1, i, -1)
        try:
            for i in range(0, 255):
                self.scr.addstr(str(i), curses.color_pair(i))
        except curses.ERR:
            # End of screen reached
            pass
        #stdscr.getch()

    def color_management(self, pair_index, fcol, bcol, attr=None):
        curses.init_pair(pair_index, fcol, bcol)

    def draw_box(self, pos_y, pos_x, len_y, len_x):
        self.scr.addstr(pos_y, pos_x, '-'*len_x) #horizontal
        self.scr.addstr(pos_y + len_y - 1, pos_x, '-'*len_x) #horizontal
        [self.scr.addstr(pos_y + i, pos_x, '|') for i in range(len_y)] # vertical
        [self.scr.addstr(pos_y + i, pos_x + len_x - 1, '|') for i in range(len_y)] # vertical
        self.scr.addstr(pos_y, pos_x, '+')
        self.scr.addstr(pos_y + len_y - 1, pos_x, '+')
        self.scr.addstr(pos_y, pos_x + len_x - 1, '+')
        self.scr.addstr(pos_y + len_y - 1, pos_x + len_x - 1, '+')
    def put_text(self, pos_y, pox_x, text, limit):
        i = 0
        line = 0
        while len(text) - i - limit > 0:
            j = text.rfind(' ', i, i+limit)
            self.scr.addstr(pos_y + line, pox_x, text[i:j])
            i = j+1
            line += 1
            #sleep(fr)
        self.scr.addstr(pos_y + line, pox_x, text[i:])
        #sleep(fr)
    def clear_box(self, pos_y, pos_x, len_y, len_x):
        for i in range(len_y):
            self.scr.addstr(pos_y + i, pos_x,' '*len_x)

    def put_ch(self, y, x, ch):
        self.scr.addstr(y, x, ch)
    
    def put_img(self, y, x, matrix, colors):
        #print(curses.color_pair(3))
        for i,row in enumerate(matrix):
            for j,ch in enumerate(row):

                if ch in colors:
                    self.scr.addstr(y + i, x + j, ch, curses.color_pair(colors[ch]))
                else: self.scr.addstr(y + i, x + j, ch, curses.color_pair(0))
        #self.scr.refresh()

    def getkey(self):
        return self.scr.getch() # use getch
    
def main():
    screen = Screen()    
    while screen.getkey() != ord('q'):
        #sleep(5)
        #screen.scr.addstr(0, 0, "Current mode: Typing mode",
        #      curses.A_REVERSE)
        screen.scr.addstr(0,0,"Pretty text", curses.color_pair(3))
        #screen.scr.addstr("caca", curses.color_pair(1))
        screen.refresh()

    curses.endwin()
if __name__ == "__main__":
    main()
#curses.wrapper(main)