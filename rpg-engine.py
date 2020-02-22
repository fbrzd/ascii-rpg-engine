import abstract
import json
from sys import argv,exit
import random
from npc import Npc

class Player:
    def __init__(self, name, meta_data_json):
        self.name = name
        self.y, self.x = meta_data_json["position"]
        self.sprite = meta_data_json["sprite"]
        
        self.max_hp = meta_data_json["hp"]
        self.hp = meta_data_json["hp"]
        self.atk = meta_data_json["atk"]
        self.money = meta_data_json["money"]
        self.items = meta_data_json["items"]
        self.clas = meta_data_json["class"]

        self.bag = meta_data_json["bag"]
        self.max_group = meta_data_json["max-group"]
        
        self.event_flags = meta_data_json["event-flags"]
        self.transports = meta_data_json["transports"]
        self.group = meta_data_json["group"]
        self.singles = meta_data_json["singles"]
        #self.group_out = meta_data_json["group-out"]
        
        self.hp_bonus = 0
        self.atk_bonus = 0
        self.bag_bonus = 0
        with open(f"{PATH}/pjs.json") as f:
            all_pjs = json.load(f)
        for m in self.group:
            self.hp_bonus = all_pjs[m]["hp"]
            self.atk_bonus = all_pjs[m]["atk"]
            self.bag_bonus = all_pjs[m]["bag"]
        
        self.max_hp = self.hp
        self.last_battle = 0
        self.repel_flag = 0
        self.poison_flag = 0

    def main_control(self):
        k = myLogic.key_control()
        flagMove = False

        # quit game
        if k == "quit":
            abstract.screen.curses.endwin()
            exit()

        # overworld-menu
        if k == "accept":
            self.menu_action()
            flagMove = True
        
        # mute game
        #elif k == "mute": abstract.Sound.toggle_mute()

        # move
        else:
            dy,dx,ly,lx = 0,0,player.currentZone.mapArray.y,player.currentZone.mapArray.x
            if player.currentZone.mapArray.cycle: update_pos = lambda dx,dy: ((self.y + dy + ly) % ly, (self.x + dx + lx) % lx)
            else: update_pos = lambda dy,dx: max(min(ly, self.y+dy),0), max(min(lx, self.x+dx),0)
            
            if k == "up": dy = -1
            if k == "down": dy = 1
            if k == "left": dx = -1
            if k == "right": dx = 1
            
            if player.currentZone.mapArray.cycle: new_y,new_x = (self.y + dy + ly) % ly, (self.x + dx + lx) % lx
            else: new_y,new_x = max(min(ly-1, self.y+dy),0), max(min(lx-1, self.x+dx),0)

            # have transport (change tiles)
            tile = player.currentZone.mapArray.current_map[new_y, new_x]
            if tile in self.transports:
                current_tile_tag,tmp_sprite = self.transports[tile]
            else:
                current_tile_tag = player.currentZone.mapArray.special_tiles[tile] if tile in player.currentZone.mapArray.special_tiles else "none"
                tmp_sprite = self.sprite

            # effects by tile
            if current_tile_tag != "col":
                flagMove = abs(self.y - new_y) + abs(self.x - new_x) > 0
                self.y, self.x = new_y,new_x
                
            
            if flagMove:
                if self.repel_flag > 0: self.repel_flag -= 1
                
                # change zone
                if (self.y, self.x) in player.currentZone.doors:
                    zone_dst,new_position = player.currentZone.doors[(self.y, self.x)]
                    player.currentZone = Zone(zone_dst, player)
                    self.y,self.x = new_position
                    player.currentZone.music.play()

                # "render"
                player.currentZone.mapArray.add_sprite(self.y, self.x, self, tmp_sprite)
                player.currentZone.mapArray.center_camera_on(self.y, self.x)

                # battle
                if current_tile_tag == "wild" and self.repel_flag == 0:
                    self.last_battle += random.choice((0,0,0,1))
                    if self.last_battle > 3:
                        self.last_battle = 0
                        if player.currentZone.enemies:
                            randomMonster = random.choice(player.currentZone.enemies)
                            battle(self, randomMonster)
                            player.currentZone.mapArray.center_camera_on(self.y, self.x)

                # tile damage
                if current_tile_tag == "hurt": self.hp -= 1
                
                # tile heal
                if current_tile_tag == "heal": self.hp = min(self.hp + 1, self.max_hp)
            
        self.show_info()
        return flagMove   
    def show_info(self):
        infos = [f"{self.name}:",
                 f"hp  {self.hp}/{self.max_hp-self.hp_bonus}{'+'*bool(self.hp_bonus)}",
                 f"atk {self.atk-self.atk_bonus}{'+'*bool(self.atk_bonus)}",
                 f"$   {self.money}",
                 "",
                 f"items {len(self.items)}/{self.bag-self.bag_bonus}{'+'*bool(self.bag_bonus)}",
                 f"group {len(self.group)}/{self.max_group}"]
        myLogic.information(infos)
    def menu_action(self):
        action = myLogic.menu("", ("interact","items","group"))
        if action == 0:
            for npc in player.currentZone.npcs:
                if abs(npc.y - self.y) + abs(npc.x - self.x) == 1:
                    npc.interact(self)
                    break
        if action == 1:
            if not len(player.items): return None
            options = list(map(lambda x: f"{x} x{self.items.count(x)}", set(self.items)))
            item = myLogic.menu(f"", options)
            if item == -1: return None # back main menu
            
            item = options[item]
            item = item[:item.rfind('x')-1]
            use_item_zone(item, player)
        if action == 2: # group
            with open(f"{PATH}/pjs.json") as f:
                all_pjs = json.load(f)
            for name_member,data_member in all_pjs.items():
                if name_member in self.group:
                    for chat in data_member["chats"]:
                        flag_exist = True
                        for flag,value in chat["event-conditions"].items():
                            if player.event_flags[flag] != value: flag_exist = False
                        if flag_exist:
                            myLogic.message(f"{name_member}: {chat['text']}")

    def add_member(self, name_member):
            if len(player.group) < player.max_group:# and name_member not in player.group:
                with open(f"{PATH}/pjs.json") as f:
                    member = json.load(f)[name_member]
                
                player.group.append(name_member)
                player.max_hp += member["hp"]
                player.hp += member["hp"]
                player.hp_bonus += member["hp"]
                
                player.atk += member["atk"]
                player.atk_bonus += member["atk"]
                
                player.bag += member["bag"]
                player.bag_bonus += member["bag"]
                
                player.money += member["money"]
                player.clas.append(member["class"])
                myLogic.message(f"{name_member} joins to group!")
            else: myLogic.message("group full...!")
            player.show_info()
    def save(self):
        with open(f"{PATH}/saves.json") as f:
            data = json.load(f)
        data[self.name] = {
            "sprite":self.sprite,
            "zone":self.currentZone.name,
            "position":(self.y,self.x),
            "class":self.clas,
            "hp":self.max_hp,# - sum(map(lambda x: x[0], self.group.values())),
            "atk":self.atk,# - sum(map(lambda x: x[1], self.group.values())),
            "money":self.money,
            "items":self.items,
            "bag":self.bag,
            "max-group":self.max_group,
            "event-flags":self.event_flags,
            "transports":self.transports,
            "singles":self.singles,
            "group":self.group
        }
        with open(f"{PATH}/saves.json", 'w') as f:
            #json.dump(data, f)
            json.dump(data, f, indent=4, sort_keys=True)

class Enemy:
    def __init__(self, name, battle_background):
        with open(f"{PATH}/pjs.json") as f:
            data_enemy = json.load(f)[name]
        
        self.name = name
        self.hp = data_enemy["hp"]
        self.max_hp = self.hp
        self.atk = data_enemy["atk"]
        self.money = data_enemy["money"]
        self.actions = data_enemy["actions"]
        self.flags = data_enemy["flags"]
        self.clas = list()

        # posible turn
        if "turn" in data_enemy: self.turn = data_enemy["turn"]
        
        # check group
        if "group" in self.flags:
            self.hp = 0
            self.atk = 0
            with open(f"{PATH}/pjs.json") as f:
                all_data = json.load(f)
            for i,e in enumerate(data_enemy["group"]):
                battle_background.add_sprite(2, 7 - len(data_enemy["group"])//2 + i, i, all_data[e]["sprite"])
                self.hp += all_data[e]["hp"]
                self.atk += all_data[e]["atk"]
                self.clas.append(all_data[e]["class"])
        else:
            battle_background.add_sprite(2, 7, 0, data_enemy["sprite"])
            self.clas.append(data_enemy["class"])

class Npc:
    def __init__(self, json_data):
        self.id = json_data["id"]
        self.y, self.x = json_data["position"]
        self.sprite = json_data["sprite"]
        self.move = json_data["move"]
        self.single = json_data["single"]
        self.interact_parameters = json_data["interact"]
    
    def interact(self, player):
        interact_type = self.interact_parameters["type"]
        interact_done = False

        if interact_type == "talk":
            myLogic.message(self.interact_parameters["text"])
            interact_done = True
        
        if interact_type == "save":
            o = myLogic.menu(self.interact_parameters["text"], ("yes", "no"))
            if o == 0:
                player.hp = player.max_hp
                player.save()
                interact_done = True

        if interact_type == "deal":
            npc_give = self.interact_parameters["give"].split(':')
            npc_take = self.interact_parameters["take"].split(':')
            if self.interact_parameters["ask"]:
                o = myLogic.menu(self.interact_parameters["text"], ("yes", "no"))
            else: myLogic.message(self.interact_parameters["text"])
            # player can
            flagGive = True
            flagTake = True
            #if npc_take[0] == "null": flagTake = True
            if npc_take[0] == "money" and player.money < int(npc_take[1]): flagTake = False
            if npc_take[0] == "item" and npc_take[1] not in player.items: flagTake = False
            if npc_give[0] == "item" and len(player.items) >= player.bag: flagGive = False
            if npc_give[0] == "member" and len(player.group) >= player.max_group: flagGive = False
            #if npc_give[0]

            if (flagGive and flagTake) and (not (self.interact_parameters["ask"]) or o == 0):
                # take from player
                if npc_take[0] == "money": player.money -= int(npc_take[1])
                if npc_take[0] == "item": player.items.remove(npc_take[1])
                
                # give to player
                if npc_give[0] == "money": player.money += int(npc_give[1])
                if npc_give[0] == "item": player.items.append(npc_give[1])
                if npc_give[0] == "transport": player.transports[npc_give[1].split(',')[0]] = npc_give[1].split(',')[1:]
                if npc_give[0] == "member": player.add_member[npc_give[1]]
                if npc_give[0] == "hp": player.max_hp = int(npc_give[1]) + player.hp_bonus
                if npc_give[0] == "atk": player.atk = int(npc_give[1]) + player.atk_bonus
                if npc_give[0] == "bag": player.bag = int(npc_give[1]) + player.bag_bonus
                
                interact_done = True
                
        if interact_type == "rush":
            if self.interact_parameters["ask"]:
                o = myLogic.menu(self.interact_parameters["text"], ("yes", "no"))
            else: myLogic.message(self.interact_parameters["text"])
            
            if not (self.interact_parameters["ask"]) or o == 0:
                myLogic.message(self.interact_parameters["text"])
                if battle(player, self.interact_parameters["enemy"]):
                    interact_done = True
                player.currentZone.mapArray.center_camera_on(self.y, self.x)
        
        if interact_type == "chap":
            if self.interact_parameters["ask"]:
                o = myLogic.menu(self.interact_parameters["text"], ("yes", "no"))
            else: myLogic.message(self.interact_parameters["text"])
            # editables
            if not (self.interact_parameters["ask"]) or o == 0:
                for key,val in self.interact_parameters["player"]:
                    if key == "zone": player.currentZone = Zone(val, player)
                    if key == "position": player.y,player.x = val
                    if key == "hp": player.hp = int(val)
                    if key == "atk": player.atk = int(val)
                    if key == "bag": player.bag = int(val)
                    if key == "max-group": player.max_group = int(val)
                    if key == "money": player.money = int(val)
                    if key == "items": player.items = val
                    if key == "sprite": player.sprite = val
                # set group & hide vars
                player.group = list()
                player.hp_bonus, player.atk_bonus,player.bag_bonus = 0,0,0
                player.clas = list()
                player.max_hp = self.hp
                player.last_battle = 0
                player.repel_flag = 0
                player.poison_flag = 0
                # reload
                player.currentZone.music.play()
                player.currentZone.mapArray.add_sprite(player.y,player.x,player,player.sprite)
                interact_done = True
        
        if interact_type == "luck":
            pass # random effect from list (interact recursive?) # maybe games generic: cards, pachisi, tracks, slot-machines

        if interact_type == "tool":
            aux = self.interact_parameters["type"]
            self.interact_parameters["type"] = self.interact_parameters["sub-type"]
            interact(player)
            self.interact_parameters["type"] = aux
            #interact_done == False

        if interact_done and "event-flags" in self.interact_parameters:
            for flag,value in self.interact_parameters["event-flags"].items():
                player.event_flags[flag] = value
            player.currentZone.reload(player)
        if interact_done and self.single:
            player.singles.append(self.id)
            player.currentZone.reload(player)

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

class Zone:
    def __init__(self, name, player):
        self.name = name
        with open(f"{PATH}/zones/{self.name}.json") as f:
            data = json.load(f)
        self.namefile = f"{PATH}/{data['meta']['namefile']}"
        self.music = abstract.Sound(f"{PATH}/{data['meta']['music']}")
        self.enemies = data["meta"]["enemies"] # class fighther, load too early?
        self.mapArray = abstract.MapArray(self.namefile, (0,0,10,30), cycle=data["meta"]["cycle"])
        self.mapArray.special_tiles = data["meta"]["tiles"]
        
        self.doors = dict()
        self.npcs = list()
        for door in data["doors"]:
            flag_exist = True
            for flag,value in door["event-conditions"].items():
                if player.event_flags[flag] != value: flag_exist = False
            if flag_exist:
                self.doors[tuple(door["position"])] = (door["zone-dst"],door["new-position"])
        for npc in data["npcs"]:
            flag_exist = True
            for flag,value in npc["event-conditions"].items():
                if player.event_flags[flag] != value: flag_exist = False
                if npc["id"] in player.singles: flag_exist = False
            if flag_exist:
                n = Npc(npc)
                self.mapArray.add_sprite(n.y, n.x, n.id, n.sprite)
                self.npcs.append(n)
    
    def reload(self, player):
        
        old_npcs = dict(map(lambda n: (n.id, (n.y, n.x)), self.npcs))
        with open(f"{PATH}/zones/{self.name}.json") as f:
            data = json.load(f)
        
        self.doors = {}
        for door in data["doors"]:
            flag_exist = True
            for flag,value in door["event-conditions"].items():
                if player.event_flags[flag] != value: flag_exist = False
            if flag_exist:
                self.doors[tuple(door["position"])] = (door["zone-dst"],door["new-position"])
        
        self.mapArray = abstract.MapArray(self.namefile, (0,0,10,30), cycle=data["meta"]["cycle"])
        self.mapArray.special_tiles = data["meta"]["tiles"]
        
        npcs = data["npcs"]
        self.npcs = []
        
        for data_npc in npcs:
            flag_exist = True
            for flag,value in data_npc["event-conditions"].items():
                if player.event_flags[flag] != value: flag_exist = False
                if data_npc["id"] in player.singles: flag_exist = False
            if flag_exist:
                n = Npc(data_npc)
                if n.id in old_npcs: n.y, n.x = old_npcs[n.id]
                self.mapArray.add_sprite(n.y, n.x, n.id, n.sprite)
                self.npcs.append(n)
        
        self.mapArray.add_sprite(player.y, player.x, player, player.sprite)

    def remove_npc(self, npc):
        self.npcs.remove(npc)
        del self.mapArray.sprites[npc.id]

# aux functions
def battle(player, name_enemy):
    # init background
    battle_background = abstract.MapArray(camera=(2,7,6,17),cycle=True)
    
    player.last_battle = 0
    enemy = Enemy(name_enemy, battle_background)
    battle_background.set_camera(0,0)

    turns = [0,1]
    while 1:
        # select action
        action_p = myLogic.menu(f"a {enemy.name}, what does?", ("atk","item","run"))
        
        if action_p == 1:
            if not len(player.items): continue
            options = list(set(player.items))
            options = list(map(lambda x: f"{x} x{player.items.count(x)}", set(player.items)))
            item = myLogic.menu(f"", options)
            if item == -1: continue # back main menu
            item = options[item]
            item = item[:item.rfind('x')-1]
        
        if action_p == 2 or action_p == -1:
            if random.randrange(2) and "boss" not in enemy.flags:
                myLogic.message("you flee way...")
                return 0
            else: myLogic.message("cant flee!")
            
        # menu enemy
        action_e = random.choice(enemy.actions)

        random.shuffle(turns)
        for i in turns:
            # player
            if i == 0:
                if action_p == 0:
                    damage = int(player.atk * random.uniform(0.7, 1.3))
                    # damage weaks fix, "<ally> make extra damage"
                    enemy.hp -= damage
                    myLogic.message(f"you hit {enemy.name} {damage} hp!")
                if action_p == 1:
                    use_item_battle(item, player, enemy)
                
            # enemy
            if i == 1:
                if action_e == "atk":
                    damage = int(enemy.atk * random.uniform(0.7, 1.3))
                    # damage weaks fix, "<ally> receive extra damage"
                    player.hp -= damage
                    player.show_info()
                    myLogic.message(f"{enemy.name} hit you {damage} hp!")
                if action_e == "heal":
                    enemy.hp = min(enemy.hp + enemy.max_hp//2, enemy.max_hp)
                    myLogic.message(f"{enemy.name} heals!")
                if action_e == "run":
                    myLogic.message(f"{enemy.name} flees away")
                    return 0
                if action_e == "turn":
                    battle_background.sprites = {}
                    myLogic.message(f"{enemy.name} turn into... {enemy.turn}!")
                    current_hp = enemy.hp
                    enemy = Enemy(enemy.turn, battle_background)
                    enemy.hp = current_hp
                    battle_background.set_camera(0,0)
                if action_e == "wait":
                    myLogic.message(f"{enemy.name} is waiting...")

            # player win
            if player.hp > 0 and enemy.hp <= 0:
                player.money += enemy.money
                myLogic.message(f"win! you earn ${enemy.money}!")
                return 1
            
            # player lose
            if player.hp <= 0: return 0

def start_management(name):
    with open(PATH + "/saves.json") as f:
        saves_data = json.load(f)
    
    # make player
    with open(PATH + "/meta.json") as f:
        meta_data = json.load(f)
    if name in saves_data: data_player = saves_data[name]
    else: data_player = meta_data["player"]
    player = Player(name, data_player)

    # ascii
    myLogic = abstract.init_env(meta_data["formats"])
    player.currentZone = Zone(data_player["zone"], player)
    player.currentZone.mapArray.add_sprite(player.y, player.x, player, player.sprite)
    player.currentZone.mapArray.center_camera_on(player.y, player.x)
    player.currentZone.music.play()
    return myLogic, player

def use_item_zone(item, player):
    myLogic.message(f"use {item}...")
    used = False
    with open(f"{PATH}/items.json") as f:
        data_item = json.load(f)[item]
    if not data_item["zone"]:
        myLogic.message("cant use this here!")
        return False
    
    t = data_item["type"]
    if t == "repel":
        player.repel_flag += data_item["value"]
        myLogic.message(f"the enemies will be repelled {player.repel_flag} steps")
        used = True
    if t == "heal":
        tmp = min(player.max_hp, player.hp + data_item["value"])
        myLogic.message(f"heal {tmp-player.hp} hp!")
        player.hp = tmp
        used = True
    if t == "back":
        with open(f"{PATH}/saves.json") as f:
            saves_data = json.load(f)
        if player.name in saves_data:
            myLogic.message("back to last checkpoint!")
            data_player = saves_data[player.name]
            player.y,player.x = data_player["position"]
            player.currentZone = Zone(data_player["zone"], player)
            player.currentZone.mapArray.add_sprite(player.y, player.x, player, player.sprite)
            player.currentZone.mapArray.center_camera_on(player.y, player.x)
            player.currentZone.music.play()
            used = True
        else: myLogic.message("not saved yet...")
    if t == "tool":
        for npc in player.currentZone.npcs:
            if npc.interact_parameters["type"] == "tool" and player.y == npc.y and player.x == npc.x:
                npc.interact(player)
                used = True
    # check uses
    if used:
        player.items.remove(item)
        player.show_info()
    return used

def use_item_battle(item, player, enemy):
    myLogic.message(f"use {item}...")
    with open(PATH+"/items.json") as f:
        data_item = json.load(f)[item]
    if not data_item["battle"]:
        myLogic.message("cant use this here!")
        return False
    
    t = data_item["type"]
    if t == "hit":
        enemy.hp -= data_item["value"]
        myLogic.message(f"cause {data_item['value']} damage to enemy!")
    if t == "heal":
        tmp = min(player.max_hp, player.hp + data_item["value"])
        myLogic.message(f"heal {tmp-player.hp} hp!")
        player.hp = tmp
    if t == "catch":
        if "catch" not in enemy.flags:
            myLogic.message(f"{item} not works on {enemy.name}...?")
        elif random.randrange(100) < data_item["value"]:
            player.add_member(enemy.name)
            enemy.hp = 0
            enemy.money = 0
        else: myLogic.message("...fail!")

    # check uses
    player.items.remove(item)
    player.show_info()
    return True

abstract.Sound.mute = "-mute" in argv
PATH = input("game folder: ")
myLogic,player = start_management(input("name player: "))
flagMove = False

# main loop
while player.hp > 0 and not player.event_flags["win"]:
    if flagMove:
        # update zone's npcs
        for n in player.currentZone.npcs:
            n.ia_move(player.currentZone)
        player.currentZone.mapArray.center_camera_on(player.y, player.x)
    
    flagMove = player.main_control()

# end
if player.hp <= 0:
    with open(PATH + "/meta.json") as f:
        abstract.Sound(PATH + '/' + json.load(f)["music-die"]).play()
    myLogic.message(f"{player.name} die...!")
elif player.event_flags["win"]:
    with open(PATH + "/meta.json") as f:
        abstract.Sound(PATH + '/' + json.load(f)["music-win"]).play()
    myLogic.message(f"{player.name} win! finish the game!")

abstract.screen.curses.endwin()