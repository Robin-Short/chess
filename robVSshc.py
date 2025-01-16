
from IPython import get_ipython
get_ipython().magic('clear')
import prova

game = prova.Partita(Site = 'Computer di Robin - Locale', Round = '1', 
                     White = 'Robin', Black = 'Claudio')
game.gioca()
game.salvaPGN('Robin-Claudio')
print(game)