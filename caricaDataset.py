import chesslib8

games = []

game = chesslib8.Partita.caricaPGN('Dataset/Partita6')

for i in chesslib8.tqdm(range(1,20)):
    game = chesslib8.Partita.caricaPGN('Dataset/Partita'+str(i))
    games.append(game)
    
lingueList = {}
for game in games:
    if not game.lingua in lingueList:
        lingueList[game.lingua] = 1
    else:
        lingueList[game.lingua] += 1
        
for game in games:
    print(game.esito)