import chesslib8 as cl
from IPython import get_ipython
get_ipython().magic('clear')

pl1 = 'Robin'
pl2 = 'PC'
#game = cl.Partita(mode = '1p',White = pl1, Black = pl2)
#game.gioca()
#salva = input('Vuoi salvare la partita?\n1)Sì\n2)No\n')
#if salva == '1':
#    nome = input('Scegli il nome da dare al file: ')
#    game.salvaPGN(nome)
'''Parti da una siciliana'''
game = cl.Partita(mode = '1p')
game.gioca(['e2e4','c7c5']) 
# oppure
#game = cl.Partita()
#game.gioca(['♙e4', '♟c5']) 
# oppure
#game = cl.Partita(lingua = 'Italiano')
#game.gioca(['Pe4', 'Pc5']) 
#game.gioca(['e4', 'c5']) QUESTO INVECE NON VA BENE!
