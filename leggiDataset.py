import chesslib8

file = open('archive/lichess_db_standard_rated_2014-08.pgn','r')
lines = file.readlines()
indiciTaglio = [0]
for i in chesslib8.tqdm(range(len(lines))):
    line = lines[i]
    if line[:6] == '[Event':
        indiciTaglio.append(i)
for j in range(2000):
    i1 = indiciTaglio[j]; i2 = indiciTaglio[j+1]
    txt = ''
    for line in lines[i1:i2]:
        txt += line
    fileNew = open('Dataset/Partita'+str(j)+'.pgn','w')
    fileNew.write(txt)
    fileNew.close()