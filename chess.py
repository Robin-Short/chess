'''PNG from <a target="_blank" href="https://icons8.com/icon/1018/re">Re</a> icon by <a target="_blank" href="https://icons8.com">Icons8</a>'''

import chesslibGraphic as cl
import pyglet
from pyglet.window import key
from pyglet.window import mouse
from pyglet import shapes
from os import walk

tipo = 'a' # tipo in 'ab'

def aggiustaMosse(mosse):
    lista = []
    stringa = ''; hoAppenaAppeso = False
    for i in range(len(mosse)):
        hoAppenaAppeso = False
        if not i % 2:
            stringa += str(i // 2 + 1) + '. '
        stringa += str(mosse[i]) + '\t'
        i += 1
        if not i % 8:
            lista.append(stringa)
            stringa = ''
            hoAppenaAppeso = True
    if not hoAppenaAppeso:
        lista.append(stringa)
    return lista

def salva(nome = None):
    global pgns
    print('Sto Salvando')
    filenames = next(walk('partiteSalvate'), 
                         (None, None, []))[2]  
    pgns = []; names = [];
    for name in filenames:
        if name[-4:] == '.pgn':
            pgns.append(name); names.append(name[:-4])
    if nome == None:
        i = 0
        while 'partita'+str(i) in names or 'partita0'+str(i) in names:
            i += 1
        nome = 'partita'+str(i) if len(str(i)) == 2 else 'partita0'+str(i)
    if nome in pgns or nome in names:
        print('eccheccazzo')
        return
    print('Nome File:', nome)
    game.salvaPGN('partiteSalvate/'+nome)
    pgns.append(nome)
    pgns.sort()
    for i in range(len(pgns)):
        filename = pgns[i]
        pgnsLabels.append(pyglet.text.Label(filename, x = 1050, y = HEIGHT - D - 120 - 20 * i, batch = pgnsNames))
    
def carica(nome = ''):
    cl.Partita.caricaPGN(nome)
    

def draw(scacchiera):
    sprites = []
    possibles = []
    if len(mossa) == 2:
        mossePossibili = game.mossePossibili()
        for m in mossePossibili:
            if m[:2] == mossa:
                possibles.append(m[2:4])
    for i in range(1,9):
        for a in cl.lettere:
            j = cl.letters2ind(a)
            d, l = D + (i-1) * 100, L + (j-1) * 100
            if tipo == 'a':
                cellColor = (102, 51, 0) if (i + j + 1) % 2 else (204, 102, 0)
            elif tipo == 'b':
                cellColor = (153, 153, 255) if (i + j + 1) % 2 else (255, 255, 255)
            shapes.Rectangle(l, d, 100, 100, color=cellColor).draw()
            if a+str(i) in possibles:
                rec = shapes.Rectangle(l+10, d+10, 80, 80, color=(0,255,100))
                rec.opacity = 75
                rec.draw()
            pezzo = scacchiera.getPezzo(a+str(i))
            if pezzo != None:
                txt = 'pngs/'+pezzo.nome + str(pezzo.colore)+tipo+'.png'
                img = pyglet.resource.image(txt)
                sprites.append(pyglet.sprite.Sprite(img, x = D + (j - 1) * 100, y = L + (i - 1) * 100))
    for sprite in sprites:
        sprite.draw()
    if game.checkFine():
        pyglet.text.Label(game.esito, x = L * 2 + 800, y = D, font_size = 35).draw()

WIDTH = 1440
HEIGHT = 847
D, L = 20, 20
window = pyglet.window.Window(WIDTH, HEIGHT)
pyglet.gl.glClearColor(0.5,0.5,0.5,1) 

game = cl.Partita(soloLista = True, stampa = False)
mossa = ''
pgns = []
caricando = False
filenames = next(walk('partiteSalvate'),(None, None, []))[2]  
for name in filenames:
    if name[-4:] == '.pgn':
        pgns.append(name)
pgns.sort()
nameSelect = pgns[-1]
menu = pyglet.graphics.Batch()
menuBorders = pyglet.graphics.Batch()
pgnsNames = pyglet.graphics.Batch(); pgnsLabels = []

for i in range(len(pgns)):
    filename = pgns[i]
    pgnsLabels.append(pyglet.text.Label(filename, x = 1050, y = HEIGHT - D - 120 - 20 * i, batch = pgnsNames))
indietroLabel = pyglet.text.Label('Indietro', x = 840, y = HEIGHT - D - 40, batch = menu)
nuovaLabel = pyglet.text.Label('Nuova Partita', x = 840, y = HEIGHT - D - 60, batch = menu)
graficaLabel = pyglet.text.Label('Cambia Grafica', x = 840, y = HEIGHT - D - 80, batch = menu)
salvaLabel = pyglet.text.Label('Salva', x = 840, y = HEIGHT - D - 100, batch = menu)
caricaLabel = pyglet.text.Label('Carica', x = 840, y = HEIGHT - D - 120, batch = menu)
randomLabel = pyglet.text.Label('New Random', x = 840, y = HEIGHT - D - 140, batch = menu)

menuLabels = [indietroLabel, nuovaLabel, graficaLabel, salvaLabel, caricaLabel,
              randomLabel]
borders = []
for i in range(len(menuLabels)):
    borders.append(pyglet.shapes.BorderedRectangle(x = 840, y = HEIGHT - D - 40 - 20 * i, 
                                    width = 200, 
                                    height = 18, border=1, 
                                    color=(255, 255, 255), 
                                    border_color=(100, 100, 100), 
                                    batch=menuBorders))
    borders[-1].opacity = 50
for label in menuLabels:
    label.bold = True
    
def do_every_frame(dt):
    if caricando:
        pgnsNames.draw()
        

@window.event
def on_draw():
    global mossa, game
    window.clear()
    pyglet.text.Label(' X', x = 0, y = HEIGHT - 18).draw()
    if len(mossa) >= 4: # controlla promozioneee!
        game.gioca([mossa])
        mossa = ''
    pyglet.text.Label(mossa, x = 840, y = 800).draw()
    moves = aggiustaMosse(game.mosseAlgebriche)
    for i in range(len(moves)):
        raw = moves[i]
        pyglet.text.Label(raw, x = 840, y = HEIGHT // 2 - 20 * i, 
                          font_size = 16).draw()
    do_every_frame(None)
    draw(game.scacchiera)
    menu.draw()
    menuBorders.draw()
    
pyglet.clock.schedule_interval(do_every_frame,1/30)

@window.event
def on_mouse_press(x, y, button, modifiers):
    global mossa, game, tipo, caricando
    if button == mouse.LEFT:
        I, J = 1, 1
        if L <= x <= L + 800:
            if D <= y <= D + 800:
                for i in range(8):
                    if L + i * 100 <= x <= L + (i+1) * 100:
                        I = i + 1
                for j in range(8):
                    if D + j * 100 <= y <= D + (j+1) * 100:
                        J = j + 1
                mossa += cl.lettere[I-1]+str(J)
        if 2 * L + 800 <= x <= 2 * L + 800 + 200: #Menu
            if HEIGHT - D - 40 <= y <= HEIGHT - D - 20: # Indietro
                mossa = 'back'
            elif HEIGHT - D - 60 <= y <= HEIGHT - D - 40: # Nuova
                game = cl.Partita(soloLista = True, stampa = False)
            elif HEIGHT - D - 80 <= y <= HEIGHT - D - 60: # Cambia Grafica
                print('cambio Grafica')
                tipo = 'a' if tipo == 'b' else 'b'
            elif HEIGHT - D - 100 <= y <= HEIGHT - D - 80: # Salva
                print('Provo a salvare')
                salva()
            elif HEIGHT - D - 120 <= y <= HEIGHT - D - 100: # Carica
                caricando = not caricando
            elif HEIGHT - D - 140 <= y <= HEIGHT - D - 120: # Random
                mode = game.mode; 
                game = cl.Partita(soloLista = True, stampa = False, mode = '0p')
                game.gioca(); game.mode = mode;
            elif HEIGHT - D - 160 <= y <= HEIGHT - D - 140:
                pass
            elif HEIGHT - D - 180 <= y <= HEIGHT - D - 160:
                pass
        if 2 * L + 800 + 200 <= x <= 2 * L + 800 + 400 and caricando: # caricaMenu
            for i in range(len(pgns)):
                if HEIGHT - D - 120 - 20 * i <= y <= HEIGHT - D - 100 - 20 * i:
                    nameSelect = 'partita'+str(i) if len(str(i)) == 2 else 'partita0'+str(i)
                    game = cl.Partita.caricaPGN('partiteSalvate/'+nameSelect)
                    caricando = not caricando
        if x < 20 and y > HEIGHT - 20:
            window.close()

@window.event
def on_mouse_motion(x, y, dx, dy):
    if 2 * L + 800 <= x <= 2 * L + 800 + 200: #Menu
        for i in range(len(menuLabels)):
            if HEIGHT - D - 40 - 20 * i <= y <= HEIGHT - D - 20 - 20 * i:
                borders[i].opacity = 100
            else:
                borders[i].opacity = 50
    else:
                for b in borders:
                    b.opacity = 50
                
pyglet.app.run()
