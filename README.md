# ascii-rpg-engine
Engine for rpg game. No graphics, just ascii text. (Include tutorial)

## Resumen
Minimalist engine writen in python3, library required are:
- curses: for all "graphic" things
- pygame: just _mixer_ module... for sound
- json: for load world's extern data
- random: for common mechanics of rpgs (random encounter, moves, etc)
- numpy: for manipulate maps efficent and simple

Run your own game using: python3 game.py _folder-game-name_ _player-name_

Make a world just need write json files, plain text for maps and move music in folders. Some features common in rpgs:
### Supported
- random encounter by zones
- stats hp, atk, gold
- inventory for use items in overworld and battles
- transport by specific tiles
- npcs (heal/save, buy, talk, battle, give transports)
- register of custom events done (only after npc'sinteract)
- ... spawn npc by this events
- save game

### Not Supported
- party members (not yet, in planning)
- class system (not yet, in planning)
- more complex battle system (not planning)
- scripted scenes (not yet, in planning)
- spells/abilities (not yet)

## Python implementation (better explain soon)
The engine is divided in 3 "layers":
- __screen.py__: this is the "low-level" layer, here print text/chars and add colors. curses module only works here.
- __abstract.py__: this is a "middle" layer, contain the logic for make menus, messages-box & manipulate arrays for the maps.
- __game.py__: this is the "high-level" layer, here management player and zone variables. starts, saves and ends games loads by extern files.

## Tutorial to make a World (Español)

### 0. Entorno
Para este motor, un juego se define con 2 carpetas de recursos y 5 archivos json (+1 para los saves, pero que apenas es necesario editar):

- __maps/__: esta carpeta tendrá los mapas, que serán archivos en texto plano (es decir sin ningun formato especial y editables desde cualquier editor de texto).
- __music/__: esta carpeta tendrá los archivos mp3/wav que se reproducirán en bucle al momento de cargar una zona (la musica _de fondo_). esto es opcional y el juego funcionará correctamente aún sin música
- __meta.json__: este archivo define las variables iniciales para el jugador (en caso de que no exista en el archivo __saves.json__), como la posicion y zona iniciales, hp, atk, variables de eventos, etc. Tambien define archivos "extras", como la musica de victoria y derrota.
- __zones.json__: es de los archivos más importantes, pues guarda información de cada zona accesible en el juego. aqui se define el nombre de los archivos relacionados a la zona, los enemigos aleatorios, las conexiones que tiene con otras zonas y un par de conceptos que se explicarán mejor con un ejemplo ("tiles" y "cycle").
- __npcs.json__: junto a __zones.json__ es el archivo más importante. aqui se especifica una lista con todos los npcs que hay en una determinada zona. los datos por npc son: un identificador único según zona (id), la posición inicial dentro la zona, condiciones de eventos para que aparezca, la letra que se usará para representarlo en la pantalla y su forma de interactuar (esto último se explica mejor con un ejemplo).
- __monsters.json__: este archivo define los stats de un enemigo, su letra para representación (igual que los npcs), el dinero por derrotarlo, y las acciones que puede hacer (esto último no es complejo, pero el listado de acciones se indicará abajo).
- __items.json__: aqui se definen los objetos, con su tipo (de daño, curacion, etc) y un valor asociado que se utiliza según el tipo de este, además de indicadores para saber si se pueden usar en combate o fuera de él. __IMPORTANTE:__ el maximo de objetos que puede llevar el jugador, para cualquier juego, es 9; además se sugiere no incluir más de 3 objetos distintos en el juego. todo esto debido a la forma en que se muestran el inventario y las opciones en los menus. en una futura versión se espera eliminar esta restricción.

Todo esto va dentro de una carpeta con nombre libre (la cual debe estar junto al archivo "game.py"). el tutorial hace referencia a la carpeta de ejemplo "example/", en ella se incluyen alguna definiciones de zonas, items y enemigos, ademas de musica y mapas para ahorrar crear propios (aunque se sugiere modificarlos para comprobar sus efectos)

### 1. Jugador y Zona

Hoy

### 2. Enemigos y Combate

Esta semana

### 3. Cambio de Zona y Tiles

Esta semana

### 4. Npcs y Eventos

Pronto

### 5. Extras y Tips

Pronto

## Soon
- time-flag support, for simulate day/night or events by steps
- cut-scenes support, like moves scripted
- lite party-members support
- colors customized

### ... Not too soon
- animations
- multiplayer
- procedural generation