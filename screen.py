from time import sleep
import threading
import curses

class Screen:
    def __init__(self, formats):

        self.scr = curses.initscr()
        self.max_Y, self.max_X = self.scr.getmaxyx()
        #self.colors = dict() # palette

        curses.start_color() # use colors
        #curses.use_default_colors()
        curses.noecho() # no echo
        curses.cbreak() # not buffer
        curses.curs_set(0) # no blink cursor
        #self.scr.nodelay(1) # getch not blocking... check "halfdelay"
        curses.halfdelay(5)
        self.scr.keypad(1) # special keys

        colors_default = {
            "black": curses.COLOR_BLACK,
            "red": curses.COLOR_RED,
            "green": curses.COLOR_GREEN,
            "yellow": curses.COLOR_YELLOW,
            "blue": curses.COLOR_BLUE,
            "magenta": curses.COLOR_MAGENTA,
            "cyan": curses.COLOR_CYAN,
            "white": curses.COLOR_WHITE
        }
        attrs_default = {
            "bold": curses.A_BOLD,
            "underline": curses.A_UNDERLINE,
            "blink": curses.A_BLINK,
            "dim": curses.A_DIM
        }
        self.formats = {}
        i = 1
        for ch,values in formats.items():
            curses.init_pair(i, colors_default[values["font"]], colors_default[values["back"]])
            tmp_color = curses.color_pair(i)
            for a in values["attrs"]:
                tmp_color = tmp_color | attrs_default[a]
            self.formats[ch] = tmp_color
            i += 1

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
    def put_text(self, pos_y, pox_x, limit_y, limit_x, text):
        i = 0
        line = 0
        while len(text) - i - limit_x > 0:
            j = text.rfind(' ', i, i+limit_x)
            self.scr.addstr(pos_y + line, pox_x, text[i:j])
            i = j+1
            line += 1
            if line == limit_y: return i
        self.scr.addstr(pos_y + line, pox_x, text[i:])
        return len(text)
    def clear_box(self, pos_y, pos_x, len_y, len_x):
        for i in range(len_y):
            self.scr.addstr(pos_y + i, pos_x,' '*len_x)

    def put_ch(self, y, x, ch):
        self.scr.addstr(y, x, ch)
    def put_img(self, y, x, matrix):
        for i,row in enumerate(matrix):
            for j,ch in enumerate(row):
                if ch in self.formats:
                    self.scr.addstr(y + i, x + j, ch, self.formats[ch])
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