import screen
import numpy as np
from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
from pygame import mixer

class Sound:
    def __init__(self,nf):
        self.nf = nf
    def play(self):
        if not self.mute:
            try:
                mixer.music.load(self.nf)
                mixer.music.play(-1)
            except:
                pass

class MapArray:
    def __init__(self, namefile=None, camera=(0,0,10,30), cycle=False):
        if namefile == None:
            self.current_map = np.full((camera[2]-2, camera[3]-2), ' ', dtype=str)
        else:
            with open(namefile) as f:
                self.current_map = np.array([ list(word.strip()) for word in f.readlines() ])
        #print(self.current_map)
        self.y, self.x = self.current_map.shape
        self.sprites = dict()
        self.camera = (camera[0]+1, camera[1]+1, camera[2]-2, camera[3]-2)
        #self.current_camera_position = (0,0)
        self.special_tiles = dict()
        #self.colors = dict()
        self.cycle = cycle

        # draw border
        SCREEN.draw_box(camera[0], camera[1], camera[2], camera[3])

    def check_tile(self, y, x):
        ch = self.current_map[y%self.y, x%self.x]
        if ch in self.special_tiles: return self.special_tiles[ch]
        else: return "none"
    def set_camera(self, pos_y, pos_x):
        y,x,ly,lx = self.camera
        buffer_map = np.array(self.current_map)
        for (ch, vector) in self.sprites.values():
            buffer_map[tuple(vector)] = ch
        
        if self.cycle:
            pos_x = (pos_x + self.x) % self.x
            pos_y = (pos_y + self.y) % self.y
        
            aux_y = min(buffer_map.shape[0], pos_y + ly)
            aux_x = min(buffer_map.shape[1], pos_x + lx)
            offset_y = ly - (aux_y - pos_y)
            offset_x = lx - (aux_x - pos_x)
            tmp1_map = np.array(buffer_map[pos_y: aux_y, pos_x: aux_x]) 
            tmp1_map = np.hstack((tmp1_map, np.array(buffer_map[pos_y: aux_y, : offset_x])))
            tmp2_map = np.hstack((np.array(buffer_map[: offset_y, pos_x: aux_x]),
                np.array(buffer_map[: offset_y, : offset_x])))
            buffer_map = np.vstack((tmp1_map, tmp2_map))
        else:
            pos_y = max(min(pos_y, self.y - ly),0)
            pos_x = max(min(pos_x, self.x - lx),0)
            
            buffer_map = np.array(buffer_map[pos_y: pos_y + ly, pos_x: pos_x + lx])
        #self.current_camera_position = pos_y,pos_x
        SCREEN.put_img(y, x, buffer_map)
    def add_sprite(self, y, x, ids, ch):
        self.sprites[ids] = (ch, np.array([y, x]))
    def mov_sprite(self, ids, y, x):
        self.sprites[ids][1][0] = y
        self.sprites[ids][1][1] = x
    def refresh(self):
        self.camera()
        SCREEN.refresh()
    def center_camera_on(self, y, x):
        self.set_camera(y - self.camera[2]//2, x - self.camera[3]//2)

class Logic:
    def __init__(self):
        #SCREEN = screen.Screen()
        self.message_box = (9,0,5,30) # y,x,ly,lx
        self.info_box = (0,29,10,13) # y,x,ly,lx
        #self.main_box = (0,0,10,30) # y,x,ly,lx
        self.menu_box = (9,29,5,13) # y,x,ly,lx
        
        # frist (& unique) draw
        SCREEN.draw_box(9,0,5,30) # text
        SCREEN.draw_box(0,29,10,13) # info
        #SCREEN.draw_box(0,0,10,30) # show
        SCREEN.draw_box(9,29,5,13) # menu

        self.button_down = 258 # key down
        self.button_up = 259 # key up
        self.button_left = 260 # key left
        self.button_right = 261 # key right
        
        self.button_accept = ord('z')
        self.button_cancel = ord('x')
        self.button_quit = ord('q')
        self.button_mute = ord('m')
    
    def menu_3(self, text, options):
        y1,x1,ly1,lx1 = self.message_box
        SCREEN.put_text(y1+1, x1+1, ly1-2, lx1-2, text)

        y2,x2,ly2,lx2 = self.menu_box
        #SCREEN.put_text(y2+1, x2+2, ' '.join(options), max(map(len,options)))#lx2-3)
        for i,op in enumerate(options):
            SCREEN.put_ch(y2+1+i, x2+2, op)

        cur_opt = 0
        SCREEN.put_ch(y2 + 1 + cur_opt, x2 + 1, '>')
        while 1:
            key = SCREEN.getkey()
            if key == self.button_accept: break
            if key == self.button_down:
                SCREEN.put_ch(y2 + 1 + cur_opt, x2 + 1, ' ')
                cur_opt = (cur_opt + 1) % len(options)
                SCREEN.put_ch(y2 + 1 + cur_opt, x2 + 1, '>')
                SCREEN.put_ch(y2+1+i, x2+2, op)
            #    SCREEN.refresh()
            elif key == self.button_up:
                SCREEN.put_ch(y2 + 1 + cur_opt, x2 + 1, ' ')
                cur_opt = (cur_opt - 1 + len(options)) % len(options)
                SCREEN.put_ch(y2 + 1 + cur_opt, x2 + 1, '>')
            elif key == self.button_cancel:
                cur_opt = -1
                break
        
        SCREEN.clear_box(y1+1, x1+1, ly1-2, lx1-2)
        SCREEN.clear_box(y2+1, x2+1, ly2-2, lx2-2)
        SCREEN.refresh()
        return cur_opt
    
    def menu(self, text, options):
        y1,x1,ly1,lx1 = self.message_box
        SCREEN.put_text(y1+1, x1+1, ly1-2, lx1-2, text)

        y2,x2,ly2,lx2 = self.menu_box
        SCREEN.put_ch(y2+1, x2+lx2//2, '^')
        SCREEN.put_ch(y2+3, x2+lx2//2, 'v')
        cur_opt = 0
        
        while 1:
            SCREEN.put_ch(y2+2, x2+lx2//2-len(options[cur_opt])//2, options[cur_opt])
            key = SCREEN.getkey()
            if key == self.button_accept: break
            
            if key == self.button_down: cur_opt = (cur_opt + 1) % len(options)
            
            if  key == self.button_up: cur_opt = (cur_opt - 1 + len(options)) % len(options)
            elif key == self.button_cancel:
                cur_opt = -1
                break
            SCREEN.put_ch(y2+2, x2+1, ' '*(lx2-2))
        
        SCREEN.clear_box(y1+1, x1+1, ly1-2, lx1-2)
        SCREEN.clear_box(y2+1, x2+1, ly2-2, lx2-2)
        SCREEN.refresh()
        return cur_opt

    def message(self, text):
        y,x,ly,lx = self.message_box
        index_remain_text = 0
        while index_remain_text != None:
            index_remain_text = SCREEN.put_text(y+1, x+1, ly-2, lx-2, text[index_remain_text:])
            #print(text[index_remain_text:])
            while 1:
                key = SCREEN.getkey()
                if key == self.button_accept or key == self.button_cancel: break
        
            SCREEN.clear_box(y+1, x+1, ly-2, lx-2)
            SCREEN.refresh()
    
    def information(self, infos):
        y,x,ly,lx = self.info_box
        SCREEN.clear_box(y+1, x+1, ly-2, lx-2)
        for i,dat in enumerate(infos):
            # add effects by type & value ?
            SCREEN.put_ch(y + i + 1, x + 1, dat)

    def key_control(self):
        key = SCREEN.getkey()
        if key == self.button_up: return "up"
        if key == self.button_down: return "down"
        if key == self.button_left: return "left"
        if key == self.button_right: return "right"
        if key == self.button_accept: return "accept"
        if key == self.button_cancel: return "cancel"
        if key == self.button_quit: return "quit"
        if key == self.button_mute: return "mute"
        return None

def init_env(formats_data):
    global SCREEN
    SCREEN = screen.Screen(formats_data)
    mixer.init()
    return Logic()

SCREEN = None