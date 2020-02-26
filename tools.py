#!/usr/bin/python3
from os import system,listdir
from sys import argv
import json

def gen_new_proyect(newpath):
    system(f"mkdir {newpath}")
    system(f"mkdir {newpath}/maps")
    system(f"mkdir {newpath}/music")
    system(f"mkdir {newpath}/zones")

    system(f"cp _templates/meta.json {newpath}/meta.json") # default values, formats, battle-system, etc
    with open(f"{newpath}/saves.json", 'w') as f: f.write('{}') # savegames
    system(f"touch {newpath}/pjs.json") # group-members (+chats), enemies random & bosses
    system(f"touch {newpath}/items.json") # items & effects

    system(f"cp _templates/zone.json {newpath}/zones/world.json")
    with open(f"{newpath}/maps/world", 'w') as f:
        f.write('\n'.join(['.'*70]*35))

def gen_zones(path, n):
    for i in range(n):
        system(f"cp _templates/zone.json {path}/zones/zone-{i+1}.json")
        with open(f"{path}/maps/zone-{i+1}", 'w') as f:
            f.write('\n'.join(['.'*33]*15))

def add_npc(path, zone, npc_type):
    try:
        with open(f"{path}/zones/{zone}.json") as f:
            data_zone = json.load(f)
        with open(f"_templates/npcs.json") as f:
            npc = json.load(f)[npc_type]
        data_zone["npcs"].append(npc)
        with open(f"{path}/zones/{zone}.json", 'w') as f:
            json.dump(data_zone, f, indent=4, sort_keys=True)
    except:
        zs = listdir(f"{path}/zones")
        print("zones:\n" + "\n".join(zs))
        with open(f"_templates/npcs.json") as f:
            npcs = json.load(f)
            print("npcs-templates:\n" + "\n".join(npcs.keys()))
        print(f"\033[31m{zone} or {npc_type} not exist!\033[0m")

def count_all(path):
    zones = listdir(f"{path}/zones")
    c_npc = 0
    with open(f"{path}/meta.json") as f:
        data = json.load(f)
        hps = [data["player"]["hp"]]
        atks = [data["player"]["atk"]]

    print(f"zones: {len(zones)}")
    for z in zones:
        with open(f"{path}/zones/{z}") as f:
            data_z = json.load(f)
        c_npc += len(data_z['npcs'])
        for n in data_z["npcs"]:
            if n["interact"]["type"] == "deal":
                if n["interact"]["give"][:2] == "hp": hps.append(int(n["interact"]["give"][3:]))
                if n["interact"]["give"][:3] == "atk": atks.append(int(n["interact"]["give"][4:]))
    atks.sort()
    hps.sort()
    print(f"npcs: {c_npc}")
    print(f"player hp: {' > '.join(map(str, hps))}")
    print(f"player atk: {' > '.join(map(str, atks))}")

mode = argv[-1]
if mode == "new":
    newpath = input("name proyect: ")
    gen_new_proyect(newpath)
    gen_zones(newpath, int(input("number of zones: ")))

if mode == "npc":
    path = input("name proyect: ")
    if path not in listdir():
        print("\033[31mproyect not exist!\033[0m")
        exit()
    while 1:
        cmd = input("<zone> <npc-template>: ").split(' ')
        if cmd[0] == "q": break
        add_npc(path, cmd[0], cmd[1])

if mode == "count":
    path = input("name proyect: ")
    count_all(path)