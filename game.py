import abstract
import json
from time import sleep
from sys import argv
import random

class Player:
    def __init__(self, name, meta_data_json):
        self.name = name
        self.y, self.x = meta_data_json["position"]
        self.sprite = 'p'
        
        self.max_hp = meta_data_json["hp"]
        self.hp = meta_data_json["hp"]
        self.atk = meta_data_json["atk"]
        self.gold = meta_data_json["gold"]
        self.items = meta_data_json["items"]
        self.max_items = 9

        self.event_flags = meta_data_json["event-flags"]
        self.transports = meta_data_json["transports"]
        self.last_battle = 0
        self.repel_flag = 0

    def main_control(self, currentZone):
        k = myLogic.key_control()
        flagMove = False

        if k == "quit":
            abstract.screen.curses.endwin()
            exit()

        # overworld-menu
        if k == "accept": self.menu_action()
        
        # move
        else:
            dy,dx,ly,lx = 0,0,currentZone.mapArray.y,currentZone.mapArray.x
            if currentZone.mapArray.cycle: update_pos = lambda dx,dy: ((self.y + dy + ly) % ly, (self.x + dx + lx) % lx)
            else: update_pos = lambda dy,dx: max(min(ly, self.y+dy),0), max(min(lx, self.x+dx),0)
            
            if k == "up": dy = -1
            if k == "down": dy = 1
            if k == "left": dx = -1
            if k == "right": dx = 1
            
            if currentZone.mapArray.cycle: new_y,new_x = (self.y + dy + ly) % ly, (self.x + dx + lx) % lx
            else: new_y,new_x = max(min(ly-1, self.y+dy),0), max(min(lx-1, self.x+dx),0)

            # have transport (change tiles)
            tile = currentZone.mapArray.current_map[new_y, new_x]
            if tile in self.transports:
                current_tile_tag,tmp_sprite = self.transports[tile]
            else:
                current_tile_tag = currentZone.mapArray.special_tiles[tile] if tile in currentZone.mapArray.special_tiles else "none"
                tmp_sprite = self.sprite

            # effects by tile
            if current_tile_tag != "col":
                flagMove = abs(self.y - new_y) + abs(self.x - new_x) > 0
                self.y, self.x = new_y,new_x
                
            
            if flagMove:
                if self.repel_flag > 0: self.repel_flag -= 1
                
                # change zone
                if (self.y, self.x) in currentZone.doors:
                    zone_dst,new_position = currentZone.doors[(self.y, self.x)]
                    currentZone = Zone(zone_dst, player)
                    self.y,self.x = new_position
                    currentZone.music.play()

                # "render"
                currentZone.mapArray.add_sprite(self.y, self.x, self, tmp_sprite)
                currentZone.mapArray.center_camera_on(self.y, self.x)

                # battle
                if current_tile_tag == "wild" and self.repel_flag == 0:
                    self.last_battle += random.choice((0,0,0,1))
                    if self.last_battle > 3:
                        self.last_battle = 0
                        if currentZone.monsters:
                            randomMonster = random.choice(currentZone.monsters)
                            battle(self, randomMonster)
                            currentZone.mapArray.center_camera_on(self.y, self.x)

                # tile damage
                if current_tile_tag == "hurt": self.hp -= 1
                
                # tile heal
                if current_tile_tag == "heal": self.hp = min(self.hp + 1, self.max_hp)
            
        self.show_info()
        return currentZone,flagMove
    
    def show_info(self):
        inventory = list(map(lambda x: f"-{x}{' '*(7-len(x))}x{self.items.count(x)}", set(self.items)))
        infos = [f"{self.name}:",
                 f"hp: {self.hp}/{self.max_hp}",
                 f"atk: {self.atk}",
                 f"g: {self.gold}",
                 f"items:"] + inventory
        myLogic.information(infos)
    def menu_action(self):
        action = myLogic.menu("", ("act","item"))
        if action == 0:
            for npc in currentZone.npcs:
                if abs(npc.y - self.y) + abs(npc.x - self.x) == 1:
                    npc.interact(self)
                    break
        if action == 1:
            if not len(player.items): return None
            options = list(set(player.items))
            item = myLogic.menu(f"", options)
            if item == -1: return None # back main menu
            
            item = options[item]
            if not use_item_zone(item, player, currentZone):
                myLogic.message("cant use this here!")

    def save(self):
        with open(PATH + "/saves.json") as f:
            data = json.load(f)
        data[self.name] = {
            "zone":currentZone.name,
            "position":(self.y,self.x),
            "hp":self.max_hp,
            "atk":self.atk,
            "gold":self.gold,
            "items":self.items,
            "event-flags":self.event_flags,
            "transports":self.transports}
        with open(PATH + "/saves.json", 'w') as f:
            json.dump(data, f)

class Npc:
    def __init__(self, json_data):
        self.id = json_data["id"]
        self.y, self.x = json_data["position"]
        self.sprite = json_data["sprite"]
        self.move = json_data["move"]
        self.interact_parameters = json_data["interact"]
    
    def interact(self, player):
        interact_type = self.interact_parameters["type"]
        
        if interact_type == "talk":
            myLogic.message(self.interact_parameters["text"])
        
        if interact_type == "menu":
            o = myLogic.menu(self.interact_parameters["text"],self.interact_parameters["options"])
            effect = self.interact_parameters["effects"][o]
            if effect == "none": pass
            if effect == "heal": player.hp = player.max_hp
        
        if interact_type == "heal":
            o = myLogic.menu(self.interact_parameters["text"], ("yes", "no"))
            if o == 0:
                player.hp = player.max_hp
                player.save()

        if interact_type == "shop":
            o = myLogic.menu(self.interact_parameters["text"], ("yes", "no"))
            if o == 0:
                if player.gold < self.interact_parameters["cost"]: myLogic.message("not have enough gold...!")
                else:
                    player.gold -= self.interact_parameters["cost"]
                    if self.interact_parameters["property"] == "item":
                        if len(player.items) < player.max_items: player.items.append(self.interact_parameters["item"])
                        else: myLogic.message("your bag is full...!")
                    if self.interact_parameters["property"] == "atk": player.atk = self.interact_parameters["atk-value"]
                    if self.interact_parameters["property"] == "hp": player.max_hp = self.interact_parameters["hp-value"]

        if interact_type == "rush":
            myLogic.message(self.interact_parameters["text"])
            battle(player, self.interact_parameters["monster"])
            currentZone.mapArray.center_camera_on(self.y, self.x)
        
        if interact_type == "transport":
            myLogic.message(self.interact_parameters["text"])
            tile,tile_tag,sprite = self.interact_parameters["transport"]
            player.transports[tile] = (tile_tag, sprite)

        if "event-flags" in self.interact_parameters:
            for flag,value in self.interact_parameters["event-flags"].items():
                player.event_flags[flag] = value

    def ia_move(self, zone):
        if self.move and random.randrange(2):
            if random.randrange(2):
                if random.randrange(2) and zone.mapArray.check_tile(self.y + 1, self.x) != "col":
                    self.y = (self.y + 1 + zone.mapArray.y) % zone.mapArray.y
                elif zone.mapArray.check_tile(self.y - 1, self.x) != "col":
                    self.y = (self.y - 1 + zone.mapArray.y) % zone.mapArray.y
            else:
                if random.randrange(2) and zone.mapArray.check_tile(self.y, self.x + 1) != "col":
                    self.x = (self.x + 1 + zone.mapArray.x) % zone.mapArray.x
                elif zone.mapArray.check_tile(self.y, self.x - 1) != "col":
                    self.x = (self.x - 1 + zone.mapArray.x) % zone.mapArray.x
            zone.mapArray.mov_sprite(self.id, self.y, self.x)
            abstract.SCREEN.refresh()

class Zone:
    def __init__(self, name, player):
        with open(PATH + "/zones.json") as f:
            data = json.load(f)[name]
        self.name = name
        self.namefile = f"{PATH}/{data['namefile']}"
        self.music = abstract.Sound(f"{PATH}/{data['music']}")
        self.monsters = data["monsters"] # class fighther, load too early?
        self.doors = dict([(tuple(door["position"]), (door["zone-dst"],door["new-position"])) for door in data["doors"]])
        
        self.mapArray = abstract.MapArray(self.namefile, (0,0,10,30), cycle=data["cycle"])
        self.mapArray.special_tiles = data["tiles"]
        self.mapArray.set_colors()
        
        with open(PATH + "/npcs.json") as f:
            npcs = json.load(f)[name]
        self.npcs = []
        
        for data_npc in npcs:
            flag_exist = True
            for flag,value in data_npc["event-conditions"].items():
                if player.event_flags[flag] != value: flag_exist = False
            if flag_exist:
                n = Npc(data_npc)
                self.mapArray.add_sprite(n.y, n.x, n.id, n.sprite)
                self.npcs.append(n)

#119
def battle(player, monster):
    player.last_battle = 0
    with open(PATH + "/monsters.json") as f:
        data_monster = json.load(f)[monster]
    max_hp_monster = data_monster["hp"]

    battle_background = abstract.MapArray(camera=(2,7,6,17),cycle=True)
    battle_background.set_colors()
    battle_background.add_sprite(2,7,0,data_monster["sprite"])
    battle_background.set_camera(0,0)

    while 1:
        
        # select action
        action = myLogic.menu(f"a {monster}, what does?", ("atk","item","run"))
        
        if action == 1:
            if not len(player.items): continue
            options = list(set(player.items))
            item = myLogic.menu(f"", options)
            if item == -1: continue # back main menu
            
            item = options[item]
            if not use_item_battle(item, player, data_monster):
                myLogic.message("cant use this in battle!")
        if action == 2 or action == -1:
            if random.randrange(2) and not data_monster["boss"]:
                myLogic.message("you flee way...")
                break
            else: myLogic.message("cant flee!")
        if action == 0:
            damage = int(player.atk * random.uniform(0.7, 1.3))
            data_monster["hp"] -= damage
            myLogic.message(f"you hit {monster}, {damage} hp!")
        
        # here ends all player's actions
        if data_monster["hp"] <= 0: break
        
        action = random.choice(data_monster["actions"])
        
        if action == "atk":
            damage = int(data_monster["atk"] * random.uniform(0.7, 1.3))
            player.hp -= damage
            player.show_info()
            myLogic.message(f"{monster} hit you {damage} hp!")
        if action == "heal":
            data_monster["hp"] = min(data_monster["hp"] + max_hp_monster//2, max_hp_monster)
            myLogic.message(f"{monster} heal his wound")
        if action == "run":
            myLogic.message(f"{monster} flees away")
            break
        if action == "turn":
            new_monster = data_monster["turn"]
            myLogic.message(f"{monster} turn into... {new_monster}!")
            monster = new_monster
            with open("monsters.json") as f:
                data_monster = json.load(f)[new_monster]
            max_hp_monster = data_monster["hp"]
        if action == "wait":
            myLogic.message(f"{monster} is waiting...")

        # here ends all enemy's actions
        if player.hp <= 0: break
    
    # define end battle
    if player.hp > 0 and data_monster["hp"] <= 0:
        player.gold += data_monster["gold"]
        myLogic.message(f"win! you earn {data_monster['gold']} gold!")
        return 1
    return 0

def start_management(name):
    myLogic = abstract.Logic()
    with open(PATH + "/saves.json") as f:
        saves_data = json.load(f)
    if name in saves_data:
        data_player = saves_data[name]
    else:
        with open(PATH + "/meta.json") as f:
            meta_player = json.load(f)
    player = Player(name, data_player)
    currentZone = Zone(data_player["zone"], player)
    currentZone.mapArray.add_sprite(player.y, player.x, player, player.sprite)
    currentZone.mapArray.center_camera_on(player.y, player.x)
    currentZone.music.play()
    return myLogic, player, currentZone

def use_item_zone(item, player, currentZone):
    with open(PATH+"/items.json") as f:
        data_item = json.load(f)[item]
    if not data_item["zone"]: return False
    
    t = data_item["type"]
    if t == "repel":
        player.repel_flag += data_item["value"]
        myLogic.message(f"the enemies will be repelled {player.repel_flag} steps")
    if t == "heal":
        tmp = min(player.max_hp, player.hp + data_item["value"])
        myLogic.message(f"heal {tmp-player.hp} hp!")
        player.hp = tmp
    
    # check uses
    player.items.remove(item)
    player.show_info()
    return True

def use_item_battle(item, player, data_monster):
    with open(PATH+"/items.json") as f:
        data_item = json.load(f)[item]
    if not data_item["battle"]: return False
    
    t = data_item["type"]
    if t == "hit":
        data_monster["hp"] -= data_item["value"]
        myLogic.message(f"cause {data_item['value']} damage to the enemy!")
    if t == "heal":
        tmp = min(player.max_hp, player.hp + data_item["value"])
        myLogic.message(f"heal {tmp-player.hp} hp!")
        player.hp = tmp

    # check uses
    player.items.remove(item)
    player.show_info()
    return True

try:
    PATH = argv[1]
    abstract.Sound.mute = "-mute" in argv
    myLogic,player,currentZone = start_management(argv[2])
    flagMove = False
except:
    abstract.screen.curses.endwin()
    print("error! syntax: python3 game.py <folder-data> <name player>")

while player.hp > 0 and not player.event_flags["win"]:
    if flagMove:
        # update zone's npcs
        for n in currentZone.npcs:
            n.ia_move(currentZone)
        currentZone.mapArray.center_camera_on(player.y, player.x)
    
    currentZone,flagMove = player.main_control(currentZone)


if player.hp <= 0:
    with open(PATH + "/meta.json") as f:
        abstract.Sound(PATH + '/' + json.load(f)["music-die"]).play()
    myLogic.message(f"{player.name} die...!")
elif player.event_flags["win"]:
    with open(PATH + "/meta.json") as f:
        abstract.Sound(PATH + '/' + json.load(f)["music-win"]).play()
    myLogic.message(f"{player.name} win! finish the game!")

abstract.screen.curses.endwin()