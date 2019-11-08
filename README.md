# ascii-rpg-engine
Engine for rpg game. No graphics, just ascii text. (Include tutorial)

## Resumen & Quick-Start
Minimalist engine writen in python3, library required are:
- curses: for all "graphic" things
- pygame: just _mixer_ module... for sound
- json: for load world's extern data
- random: for common mechanics of rpgs (random encounter, moves, etc)
- numpy: for manipulate maps efficent and simple

Run your own game using:
- from terminal, using the python's interpreter: python3 rpg-engine.py
- from terminal, using the compiled program: ./rpg-engine
then input the folder name that contains the game data, and put your player name... that's all!

Make a world just need write json files, plain text for maps and move music in folders. If not want tutorials, see the "own/" folder for a practical guide of a game "complete". Some features common in rpgs:

### Supported
- random encounter by zones
- stats hp, atk, gold
- inventory for use items in overworld and battles
- transport by specific tiles
- npcs (heal/save, buy, talk, battle, give transports, add party-members)
- register of custom events done (only after npc's interact)
- ... spawn (or not) npc by this events
- save game
- stat's bonus for party members & and his "party-chat"

### Not Supported
- class system (not yet, in planning)
- more complex battle system (not planning)
- scripted scenes (not yet, in planning)
- spells/abilities (not yet)
- text for intro/outro (very soon)

## Python implementation (better explain soon)
The engine is divided in 3 "layers":
- __screen.py__: this is the "low-level" layer, here print text/chars and add colors. curses module only works here.
- __abstract.py__: this is a "middle" layer, contain the logic for make menus, messages-box & manipulate arrays for the maps.
- __rpg-engine.py__: this is the "high-level" layer, here management player and zone variables. starts, saves and ends games loads by extern files.

## Tutorial to make a World (Español)

### 0. Entorno
Para este motor, un juego se define con 2 carpetas de recursos y 5 archivos json (+1 para los saves, pero que apenas es necesario editar):

- __maps/__: esta carpeta tendrá los mapas, que serán archivos en texto plano (es decir sin ningun formato especial y editables desde cualquier editor de texto).
- __music/__: esta carpeta tendrá los archivos mp3/wav que se reproducirán en bucle al momento de cargar una zona (la musica _de fondo_). esto es opcional y el juego funcionará correctamente aún sin música
- __meta.json__: este archivo define las variables iniciales para el jugador (en caso de que no exista en el archivo __saves.json__), como la posicion y zona iniciales, hp, atk, variables de eventos, etc. Tambien define archivos "extras", como la musica de victoria y derrota.
- __zones.json__: es de los archivos más importantes, pues guarda información de cada zona accesible en el juego. aqui se define el nombre de los archivos relacionados a la zona, los enemigos aleatorios, las conexiones que tiene con otras zonas y un par de conceptos que se explicarán mejor con un ejemplo ("tiles" y "cycle").
- __npcs.json__: junto a __zones.json__ es el archivo más importante. aqui se especifica una lista con todos los npcs que hay en una determinada zona. los datos por npc son: un identificador único según zona (id), la posición inicial dentro la zona, condiciones de eventos para que aparezca, la letra que se usará para representarlo en la pantalla y su forma de interactuar (esto último se explica mejor con un ejemplo).
- __enemies.json__: este archivo define los stats de un enemigo, su letra para representación (igual que los npcs), el dinero por derrotarlo, y las acciones que puede hacer (esto último no es complejo, pero el listado de acciones se indicará abajo).
- __items.json__: aqui se definen los objetos, con su tipo (de daño, curacion, etc) y un valor asociado que se utiliza según el tipo de este, además de indicadores para saber si se pueden usar en combate o fuera de él.

Todo esto va dentro de una carpeta con nombre libre. el tutorial hace referencia a la carpeta de ejemplo "example/", en ella se incluyen alguna definiciones de zonas, items y enemigos, ademas de musica y mapas para ahorrar crear los propios (aunque se sugiere modificarlos para comprobar sus efectos)

### 1. Jugador y Zonas
Primero debes definir cuales serán los valores _por defecto_ que tendrá el jugador, para esto edita el archivo __meta.json__: reemplaza "zone":"???" por "zone":"zone1"; esto indicará que el jugador (_por defecto_) se encuentra en la "zone1". Si ejecutas el motor con la carpeta de tu juego, aún no funcionará, pues el motor intenta buscar "zone1" en el archivo __zones.json__ y esta no se encuentra.

Para declarar la "zone1" en el archivo __zone.json__, reemplaza "name-zone-here" por "zone1" y listo ahora el jugador debería poder moverse a traves del mapa sin problemas; para modificar el mapa de esta zona fijate en la variable "namefile", esta guarda la ruta del archivo de texto con el mapa que debe cargarse. Para este ejemplo puedes ir a maps/map1 y editarlo... incluso puedes crear un archivo nuevo (map2, por ejemplo) y modificar la variable "namefile" para que en lugar de cargar "maps/map1", cargue "maps/map2". No hay límite para el tamaño de los mapas, solo asegurate que todas las lineas tengan el mismo numero de letras.

#### (Paréntesis para JSON)
Por si no estas familiarizado con json, basicamente las _llaves_ {} definen un objeto, dentro de los cuales puedes incluir variables ("nombre-de-variable" : "valor-de-la-variable"), los valores pueden ser texto (escrito entre comillas ""), numeros, booleanos (true/false), listas (valores ordenados entre _brackets_ []) y otros objetos (_llaves_ {} denuevo). Esto debería ayudarte a visualizar mejor la estructura de la información definida en los arachivos json, por ejemplo, ahora sabes que "zone1":{...} representa una variable llamada "zone1" y que registra un objeto con más variables.

Las variables de una zona, en el archivo __zones.json son:
- namefile: ruta del mapa para esa zona
- music: ruta del archivo de audio para la musica que sonará en esa zona
- tiles: aqui se definen los "tags" que tendrán ciertos caractéres de tu mapa. Por ejemplo si quieres que el caractér "#" represente un objeto sólido o _no-atravesable_, entonces incluye la variable "#":"col" dentro del objeto tiles; esto hará que el motor considere "#" como una colision (lista completa de tags al final del tutorial).
- enemies: una lista con el nombre de todos los enemies que aparecen de forma aleatoria en esa zona, prueba a incluir "zombie" (es un enemigo ya definido para el tutorial)
- cycle: es un booleano que indica si el mapa es cíclico (true) y por lo tanto si el jugador navega en una única dirección terminará dando la vuelta; ó si no lo es (false) en cuyo caso colisiona con los bordes. Prueba a modificar la zona de ejemplo.
- doors: es una lista con objetos (esto se empieza a complicar) para definir como se _conectan_ las zonas. Cada objeto de esta lista tiene 3 variables:
  - position: indica la coordenada y,x en donde se ubica la _puerta_
  - zone-dst: indica el nombre de la zona a la cual se transportará al jugador
  - new-position: indica la nueva posición del jugador (y,x) en la nueva zona

Prueba añadir una puerta en la "zone1" agregando entre los _brackets_ lo siguiente: {"position":[y1,x1], "zone-dst":"zona-destino", "new-position":[y2,x2]}. Reemplaza los valores y,x con las posiciones que creas conveniente (aprovecha la zona "zone2" ya definida para guiarte con la declaración de los tiles y las puertas).

Cosas que pueden generar confusión: los tags de los tiles y las puertas son independientes entre zonas. Ejemplo: En una zona el caracter "#" puede representar un muro infranqueable, pero en otra puede ser un techo por el que sí es posible caminar; entonces agregaríamos el tile "#" con "col" únicamente en la primera zona, la cual no afecta nada de la segunda. Para el caso de las puertas es igual: no es necesario que las coordenadas se compartan entre "pares" de puertas (esto puede aprovecharse para hacer laberintos), además tampoco es necesario que se agregue un tile con un tag _especial_ (esto puede aprovecharse para hacer puertas falsas o puertas secretas)

### 2. Enemigos y Combate
Es posible iniciar combates de 2 formas: mediante encuentros aleatorios y mediante interacción con npcs, aquí se explicará la primera.

Para agregar un enemigo aleatorio a una zona simplemente debemos editar el archivo __zones.json__ y agregar el nombre de un enemigo a la lista "enemies" de una zona, prueba agregar "zombie" dentro de los _brackets_ ("enemies":["zombie"]). Seguramente por mucho que recorras la zona no aparecerá ningun enemigo aleatorio, esto es porque el combate aleatorio se calcula únicamente si el jugador _pisa_ tiles con el tag "wild", prueba agregar algunos caractéres extra a tu mapa y luego, en el archivo __zones.json__ agrega un tile con el tag "wild" (de la misma forma que antes agregaste un tile con el tag "col")

Agregar "zombie" anteriormente fue sencillo porque el enemigo "zombie" ya estaba declarado por el tutorial; prueba declarar un nuevo tipo de enemigo e incluyelo como enemigo aleatorio: a veces aparecerá un zombie y a veces tu enemigo. Guiate por las variables definidas para el "zombie", estas son:
- hp: su vida
- atk: su ataque
- sprite: la letra con la que se le representará en el combate
- gold: el oro que deja al ser derrotado
- actions: una lista con todas las acciones que puede hacer (lista completa al final del tutorial)
- boss: booleano para saber si el enemigo es un "boss", sirve para no permitir el escape del combate

Si todo funcionó hasta ahora, seguramente te diste cuenta que el combate es muy simple... pues lo es: únicamente puedes _atacar_ (atk) _usar un objeto_ (item) o _escapar_ run. Aqui algunos detalles sobre estas acciones:
- atk: resta tu _atk_ al _hp_ del enemigo
- item: despliega un menu para usar un objeto disponible. los objetos aparecerán listados ya sea que puedas usarlos en combate o no.
- run: intenta escapar del combate (si el enemigo no es un "boss"), con 50% de exito.

Es importante tener en cuenta que la acción del jugador __siempre__ se ejecuta antes que la de los enemigos. Esto puede llegar a cambiar en futuras versiones, pero se velará por no agregar más variables relacionadas únicamente al combate.

### 3. Npcs y Eventos

Pronto

### 4. Tile-Tags, Acciones-Enemigos, Interacciones-Npcs, Items
Todos los tags para tiles (poner un tag propio __no__ romperá el juego, pero tampoco afectará en nada):
- col: el jugador y los npcs no pueden pasar por estos tiles
- hurt: el jugador pierde 1 hp cuando pasa por estos tiles
- heal: el jugador se cura 1 hp cuando pasa por estos tiles
- wild: en estos tiles puede aparecer un enemigo aleatorio de la zona

Todos las acciones de enemigos (poner una propia __si__ romperá el juego). Las acciones tienen una probabilidad proporcional al número de veces que aparezca en la lista, ejemplo: un enemigo con una lista de acciones ["atk","atk","heal"] atacará 2/3 de las veces y se curará el 1/3 restante:
- atk: el enemigo resta su _atk_ al _hp_ del jugador
- heal: el enemigo se cura la mitad de sus _hp maximos_
- wait: el enemigo espera (pasa su turno sin hacer nada)
- turn: el enemigo se transforma en otro enemigo. No cura sus hp, pero actualiza todas sus variables.
- run: el enemigo huye

Todas las interacciones de npcs (poner una propia __si__ romperá el juego), todas requieren una variable "text", algunas requieren variables extra:
- talk: muestra un mensaje con la variable "text".
- shop: muestra un mensaje con la variable "text" y abre un menu (yes/no) para decidir intercambiar _gold_, según la cantidad definida por la variable "cost", por el servicio que define la variable "property". La variable "property" puede tomar los valores "atk", "hp" ó "item"; respectivamente, fijan el atk ó el hp según la variable "atk-value" ó "hp-value", para el caso "property":"item" es necesario declarar una variable "item":"nombre-de-item".
- heal: muestra un mensaje con la variable "text" y abre un menu para elegir curar todos tus hp o no, luego de curar guarda automaticamente la partida en __saves-json__.
- rush: muestra un mensaje con la variable "text" e inicia un combate con el enemigo de la variable "enemy".
- transport: muestra un mensaje con la variable "text" y agrega un transporte para el jugador, estos se definen con tres elementos: __1)__ el tile por el cual el transporte se activa, __2)__ el nuevo tag de ese tile y __3)__ el sprite que reemplaza al del jugador en esos tiles; estos 3 elementos deben estar en el mismo orden, en una lista en la variable "transport". Por ejemplo, para agregar un transporte que __1)__ se active sobre los tiles "T", __2)__ que cure al jugador cuando pase por uno, y que __3)__ cambie el sprite del jugador a "t", agregaríamos {"T", "heal", "t"}.
- group: muestra un mensaje con la variable "text" y agrega al grupo el miembro en la variable "member", es el único momento donde se hacen efectivos los bonus para el "max_hp", "atk" y "max_items", además no se permitirá tener dos miembros con el mismo nombre

soon items...

## Soon
- better menu
- time-flag support, for simulate day/night or events by steps
- cut-scenes support, like moves scripted
- lite party-members support
- colors customized

### ... Not too soon
- animations
- multiplayer
- procedural generation