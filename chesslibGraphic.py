#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb  5 17:24:34 2022

@author: robins
"""

###############################################################################
#                                                                             #
#   Import e dichiarazioni di costanti                                        #
#                                                                             #
###############################################################################

import numpy as np
import time
import random as rn
from tqdm import tqdm
import matplotlib as mpl
import matplotlib.pyplot as plt

modalita = ['0p', '1p', '2p']
tipiMosse = ['Sposta', 'Mangia', 'Avanza1', 'Avanza2', 'Pedone Mangia',
             'Enpassant', 'Arrocco Corto', 'Arrocco Lungo', 
             'Promozione Mangia', 'Promozione Avanza']

risultati = ['0-1','1-0','1/2-1/2','*']

numeri = '12345678'
lettere = 'abcdefgh'

lingue = ('Italiano', 'English', 'Simboli')
Lingua = 'Italiano'
# ATENZIONE!! In nessuna lingua l'iniziale di un pezzo deve essere 'O':
# si confonderebbe con l'arrocco
simboliBianchi = '♙♗♘♖♕♔'
simboliNeri = '♟♝♞♜♛♚'    
simboli = '♙♗♘♖♕♔♟♝♞♜♛♚'
italiano = 'PACTDR'
english = 'PBNRQK'

if Lingua == 'Italiano':
    caratteriBianchi = 'PACTDR'
    caratteriNeri = 'PACTDR'
    caratteri = caratteriBianchi
elif Lingua == 'English':
    caratteriBianchi = 'PBNRQK'
    caratteriNeri = 'PBNRQK'
    caratteri = caratteriBianchi
else:
    caratteriBianchi = '♙♗♘♖♕♔'
    caratteriNeri = '♟♝♞♜♛♚'
    caratteri = caratteriBianchi+caratteriNeri

backGround = '\u001b[46m' 
reset = '\u001b[0m'    
l2i = {'a':1,'b':2,'c':3,'d':4,'e':5,'f':6,'g':7,'h':8}

tTot = 0
tCopia = 0              # Tempo speso acopiare i pezzi
tInitScacchiera = 0     # Non disgiunto dal precedente
tIndietro = 0
indietro = 0
ultimaPartita = None

BIANCO = 0
NERO = 1
# OSS. 1-BIANCO = NERO e 1-NERO = BIANCO

###############################################################################
#                                                                             #
#   Funzioni generiche utili                                                  #  
#                                                                             #
###############################################################################

def letters2ind(a):
    return l2i[a]

def dist(p, q): # Distanza Manhattan
    x = abs(letters2ind(p[0]) - letters2ind(q[0]))
    return x + abs(int(p[1]) - int(q[1]))

###############################################################################
#                                                                             #
#   Pezzo: Classe, metodi e funzioni                                          #
#                                                                             #
###############################################################################

class Pezzo():
    def __init__(self, pos, col, punt, nome, car, 
                 attaccaCheck = lambda pos: False, 
                 mossaLecita = lambda pos: True):
        self.posizione = pos
        self.colore = col
        self.punteggio = punt
        self.mossaLecita = mossaLecita #Funzione
        self.nome = nome
        self.carattere = car
        self.attaccaCheck = attaccaCheck
        self.storiaPosizioni = [pos]
        
    def setPosizione(self, q):
        self.posizione = q
    
    def __str__(self):
        if not self.carattere in simboli:
            for i in range(len(caratteri)):
                if caratteri[i] == self.carattere:
                    break
            #i -= 1
            if self.colore == BIANCO: return simboliBianchi[i]
            else: return simboliNeri[i]
        return self.carattere
    
    def attacca(self, scacchiera, casella):
        return self.attaccaCheck(scacchiera, self, casella)
    
    def copia(self):
        global tCopia
        t = time.time()
        tipoPezzo = type(self)
        x =  tipoPezzo(
                self.posizione, 
                self.colore,
                self.storiaPosizioni.copy())
        tCopia += time.time() - t
        return x
        
    def mossePossibili(self, partita):
        mPossibili = []
        p = self.posizione
        caselle = self.getCaselleRaggiungibili()
        for q in caselle:
            mossa = p+q
            ok, tipo = partita.checkLegale(mossa)
            if ok:
                mosse = [mossa]
                if tipo in ('Promozione Avanza','Promozione Mangia'):
                    mosse = []
                    if self.colore == BIANCO: promovibili = caratteri[1:5]
                    else: promovibili = caratteri[7:11]
                    for promosso in promovibili:
                        mosse.append(mossa+promosso)
                for mossa in mosse:
                    mPossibili.append(mossa)
        return mPossibili
    
    def getCaselleRaggiungibili(self):
        caselle = []
        for a in lettere:
            for i in numeri:
                caselle.append(a+i)
        return caselle
    
    def mosso(self):
        return False if len(self.storiaPosizioni) == 1 else True
    
    def __eq__(self, pezzo):
        if type(pezzo) != type(self):
            return False
        if self.nome == pezzo.nome and self.colore == pezzo.colore:
            return True
        
class Re(Pezzo):
    def __init__(self, pos, col = BIANCO, storiaPos = False):# Brutta scelta
        cars = caratteriBianchi if col == BIANCO else caratteriNeri
        car = cars[5]
        super().__init__(pos, col, 0, 'RE', car, reAttacca, mlRe)
        if storiaPos:
            self.storiaPosizioni = storiaPos
    
    def getCaselleRaggiungibili(self):
        p = self.posizione
        caselle = []
        longitudine = [left, right, lambda p: p]
        latitudine = [up, down, lambda p: p]
        for lon in longitudine:
            q = lon(p)
            if q != None:
                for lat in latitudine:
                    r = lat(q)
                    if r != None:
                        caselle.append(r)
        if not self.mosso():
            caselleArrocco = ['c1', 'g1'] 
            if self.colore == NERO: ['c8','g8']
            caselle += caselleArrocco
        return caselle
        
class Regina(Pezzo):
    def __init__(self, pos, col = BIANCO, storiaPos = False):
        cars = caratteriBianchi if col == BIANCO else caratteriNeri
        car = cars[4]
        super().__init__(pos, col, 9, 'REGINA', car, reginaAttacca, mlRegina)
        if storiaPos:
            self.storiaPosizioni = storiaPos
        
class Torre(Pezzo):
    def __init__(self, pos, col = BIANCO, storiaPos = False):
        cars = caratteriBianchi if col == BIANCO else caratteriNeri
        car = cars[3]
        super().__init__(pos, col, 5, 'TORRE', car, torreAttacca, mlTorre)
        if storiaPos:
            self.storiaPosizioni = storiaPos
    
    def getCaselleRaggiungibili(self):
        pa, p1 = self.posizione
        caselle = []
        for a in lettere:
            caselle.append(a+p1)
        for i in numeri:
            caselle.append(pa+i)
        return caselle
        
class Cavallo(Pezzo):
    def __init__(self, pos, col = BIANCO, storiaPos = False):
        cars = caratteriBianchi if col == BIANCO else caratteriNeri
        car = cars[2]
        super().__init__(pos, col, 3, 'CAVALLO', 
                         car, cavalloAttacca, mlCavallo)
        if storiaPos:
            self.storiaPosizioni = storiaPos
            
    def getCaselleRaggiungibili(self):
        p = self.posizione
        caselle = []
        longitudine = [left, right]
        latitudine = [up, down]
        for lon in longitudine:
            for lat in latitudine:
                if lon(p) != None and lat(p) != None and lat(lat(p)) != None:
                    caselle.append(lat(lat(lon(p))))
                if lat(p) != None and lon(p) != None and lon(lon(p)) != None:    
                    caselle.append(lon(lon(lat(p))))
        return caselle
        
class Alfiere(Pezzo):
    def __init__(self, pos, col = BIANCO, storiaPos = False):
        cars = caratteriBianchi if col == BIANCO else caratteriNeri
        car = cars[1]
        super().__init__(pos, col, 3, 'ALFIERE', 
                         car, alfiereAttacca, mlAlfiere)
        if storiaPos:
            self.storiaPosizioni = storiaPos
            
    def getCaselleRaggiungibili(self):
        p = self.posizione
        caselle = []
        longitudine = [left, right]
        latitudine = [up, down]
        for lon in longitudine:
            for lat in latitudine:
                q = p
                while lat(q) != None and lon(q) != None:
                    q = lat(lon(q))
                    caselle.append(q)
        return caselle
        
class Pedone(Pezzo):
    def __init__(self, pos, col = BIANCO, storiaPos = False, 
                 appenaMossoDoppio = False):
        cars = caratteriBianchi if col == BIANCO else caratteriNeri
        car = cars[0]
        super().__init__(pos, col, 1, 'PEDONE', 
                         car, pedoneAttacca, mlPedone)
        if storiaPos:
            self.storiaPosizioni = storiaPos
        self.appenaMossoDoppio = appenaMossoDoppio
        
    def copia(self):
        x = Pezzo.copia(self)
        x.appenaMossoDoppio = self.appenaMossoDoppio
        return x
    
    def getCaselleRaggiungibili(self):
        p = self.posizione
        caselle = []
        lat = up if self.colore == BIANCO else down
        q = lat(p)
        if q != None:
            caselle.append(q)
            if right(q) != None: caselle.append(right(q))
            if left(q) != None: caselle.append(left(q))
            if lat(q) != None: caselle.append(lat(q))
        return caselle

#Funzioni per shiftare le posizioni
def up(posizione):
    a, i = posizione
    i = int(i)
    return a+str(i+1) if i < 8 else None
def down(posizione):
    a, i = posizione
    i = int(i)
    return a+str(i-1) if i > 1 else None
def left(posizione):
    a, i = posizione
    if a == 'a':
        return None
    return lettere[letters2ind(a)-2]+i
def right(posizione):
    a, i = posizione
    if a == 'h':
        return None
    return lettere[letters2ind(a)]+i
        
###############################################################################
#                                                                             #
#   Scacchiera: Classe, metodi e funzioni                                     #
#                                                                             #
############################################################################### 
    
class Scacchiera():
    def __init__(self, configurazionePersonalizzata = None):
        global tInitScacchiera
        t = time.time()
        self.posizioni = []
        d = dict()
        if configurazionePersonalizzata == None:# Nuova Partita
            #Pedoni ♙♟
            for a in lettere:
                d[a+'2'] = Pedone(a+'2', BIANCO)
                d[a+'7'] = Pedone(a+'7', NERO)
            #Torri ♖♜
            d['a1'] = Torre('a1', BIANCO); d['h1'] = Torre('h1', BIANCO)
            d['a8'] = Torre('a8', NERO); d['h8'] = Torre('h8', NERO)
            #Cavalli ♘♞
            d['b1'] = Cavallo('b1', BIANCO); d['g1'] = Cavallo('g1', BIANCO)
            d['b8'] = Cavallo('b8', NERO); d['g8'] = Cavallo('g8', NERO)
            #Alfieri ♗♝
            d['c1'] = Alfiere('c1', BIANCO); d['f1'] = Alfiere('f1', BIANCO)
            d['c8'] = Alfiere('c8', NERO); d['f8'] = Alfiere('f8', NERO)
            #Regine ♕♛
            d['d1'] = Regina('d1', BIANCO)
            d['d8'] = Regina('d8', NERO)
            #Re ♔♚
            d['e1'] = Re('e1', BIANCO)
            d['e8'] = Re('e8', NERO)
        else:
            for posizione in configurazionePersonalizzata:
                cPP = configurazionePersonalizzata[posizione]
                if cPP != None:
                    d[posizione] = cPP.copia()
        self.pezzi = d
        tInitScacchiera += time.time() - t
        
    def getPezzo(self, p=None):
        if p == None:
            return self.pezzi
        else:
            if p in self.pezzi:
                return self.pezzi[p]
            else:
                return None
    
    def __str__(self):
        txt = '\n'
        for i in range(8,0,-1):
            txt += '\n ' + str(i) + ' '
            for a in lettere:
                pezzo = self.getPezzo(a+str(i))
                if pezzo == None:
                    txt += '  '
                else:
                    txt += str(pezzo)+' '
        txt += '\n   A B C D E F G H'
        return txt
    
    def stampa(self):
        txt = '\n'
        for i in range(8,0,-1):
            txt += '\n ' + str(i) + ' '
            for a in lettere:
                pezzo = self.getPezzo(a+str(i))
                if not (i + letters2ind(a)) % 2:
                    sfondo = backGround
                else:
                    sfondo = reset
                if pezzo == None:
                    txt += sfondo+'  '
                else:
                    txt += sfondo+str(pezzo)+' '
                txt += reset
        txt += '\n   A B C D E F G H \n'
        print(txt)
    
    def getPezzi(self, colore = None):
        if colore != None:
            if colore == BIANCO: return self.getBianchi()
            if colore == NERO: return self.getNeri()
            return None
        pezzi = []
        for pos in self.pezzi:
            pezzi.append(self.pezzi[pos])
        return pezzi
    
    def getBianchi(self):
        bianchi = []
        for pos in self.pezzi:
            pezzo = self.pezzi[pos]
            if pezzo.colore == BIANCO:
                bianchi.append(pezzo)
        return bianchi
    
    def getNeri(self):
        neri = []
        for pos in self.pezzi:
            pezzo = self.pezzi[pos]
            if pezzo.colore == NERO:
                neri.append(pezzo)
        return neri
    
    def getPunteggio(self):
        bianco = 0; nero = 0;
        for pos in self.pezzi:
            pezzo = self.getPezzo(pos)
            if not pezzo == None:
                if pezzo.colore == BIANCO:
                    bianco += pezzo.punteggio
                else:
                    nero += pezzo.punteggio
        return bianco, nero
    
    def getReBianco(self):
        bianchi = self.getBianchi()
        for pezzo in bianchi:
            if pezzo.nome == 'RE':
                return pezzo
        return None
    
    def getReNero(self):
        neri = self.getNeri()
        for pezzo in neri:
            if pezzo.nome == 'RE':
                return pezzo
        return None
    
    def getRe(self, colore):
        if colore == BIANCO: return self.getReBianco()
        if colore == NERO: return self.getReNero()
        return None
    
    def checkScaccoBianco(self):
        '''Ritorna True se il bianco è sottoscacco, False altrimenti'''
        neri = self.getNeri()
        re = self.getReBianco()
        q = re.posizione
        for pezzo in neri:
            if pezzo.attacca(self, q):
                return True
        return False
    
    def checkScaccoNero(self):
        '''Ritorna True se il nero è sottoscacco, False altrimenti'''
        bianchi = self.getBianchi()
        re = self.getReNero()
        q = re.posizione
        for pezzo in bianchi:
            if pezzo.attacca(self, q):
                return True
        return False
    
    def checkScacco(self, turno):
        if turno == BIANCO: return self.checkScaccoBianco()
        else: return self.checkScaccoNero()

    def sonoSottoScacco(self, turno):
        if turno == BIANCO: return self.checkScaccoBianco()  
        else: return self.checkScaccoNero()
    

#Funzioni per stabilire se un pezzo sta attaccando* una data casella
# Con attaccare si intende possibilità di sostituirsi in una casella ad un 
# pezzo avversario ipotizzato essere in posizione d'arrivo. Per i PEDONI questo
# NON coincide con la possibilità di movimento.
        
def pedoneAttacca(scacchiera, pedone, casella):
    pos = pedone.posizione
    if dist(pos, casella) != 2:
        return False
    if pedone.colore == BIANCO:
        if not up(pos) == None:
            if right(up(pos)) == casella or left(up(pos)) == casella:
                return True
    if pedone.colore == NERO:
        if not down(pos) == None:
            if right(down(pos)) == casella or left(down(pos)) == casella:
                return True
    return False

def cavalloAttacca(scacchiera, cavallo, casella):
    p = cavallo.posizione; q = casella; pa, p1, qa, q1 = p+q;
    if pa == qa or p1 == q1:
        return False
    elif dist(p,q) == 3:
        return True
    return False

def torreAttacca(scacchiera, torre, casella):
    p = torre.posizione; q = casella;
    pa, p1 = p; qa, q1 = q;
    if pa == qa and p1 != q1: 
        # Stessa Colonna
        start, end = (p, q) if p1 < q1 else (q, p)
        for i in range(int(start[1]) + 1,int(end[1])):
            if scacchiera.getPezzo(pa+str(i)) != None:
                return False
        return True
    if pa != qa and p1 == q1: 
        # Stessa Riga
        start, end = (p, q) if pa < qa else (q, p)
        for a in range(letters2ind(start[0]), letters2ind(end[0])-1):
            if scacchiera.getPezzo(lettere[a]+p1) != None:
                return False
        return True
    return False

def alfiereAttacca(scacchiera, alfiere, casella):
    p = alfiere.posizione; q = casella;
    pa, p1 = p; qa, q1 = q; 
    da = False; dd = False;
    diff = letters2ind(pa) - int(p1)
    somm = letters2ind(pa) + int(p1)
    if letters2ind(qa) - int(q1) == diff: # Diagonale Ascendente
        da = True; lon, lat = (left, down) if qa < pa else (right, up);
    if letters2ind(qa) + int(q1) == somm: # Diagonale Discendente
        dd = True; lon, lat = (left, up) if qa < pa else (right, down);
    if da or dd:
        ok = True
        start = p
        while start != q:
            start = lat(lon(start))
            if start != q and scacchiera.getPezzo(start) != None:
                ok = False; break;
        if ok: return True
    return False

def reginaAttacca(scacchiera, regina, casella):
    orVert = torreAttacca(scacchiera, regina, casella)
    diagonale = alfiereAttacca(scacchiera, regina, casella)
    return orVert or diagonale

def reAttacca(scacchiera, re, casella):
    pos = re.posizione
    if dist(pos, casella) <= 2:
        pa, p1 = pos; qa, q1 = casella
        c1 = dist(pos, casella) == 1
        c2 = dist(pos, casella) == 2
        c3 = pa != qa and p1 != q1
        return c1 or (c2 and c3)
    return False

###############################################################################
#                                                                             #
#   Partita: Classe, metodi e funzioni                                        #
#                                                                             #
###############################################################################         

class Partita():
    def __init__(self, scacchiera = None, configurazionePersonalizzata = None, 
                 mode = '2p', stampa = True, biancoAI = lambda p: randomAI(p), 
                 neroAI = lambda p: randomAI(p), Event = 'Amichevole', 
                 Site = '', Date = time.strftime("%Y.%m.%d"), Round = '?',
                 White = 'Giocatore 1', Black = 'Giocatore 2', 
                 lingua = 'Simboli', soloLista = False):
        global ultimaPartita
        ultimaPartita = self
        # Informazioni generiche
        self.Event = Event
        self.Site = Site
        self.Date = Date
        self.Round = Round
        self.White = White
        self.Black = Black
        self.Result = '*'
        # Informazioni tecniche
        self.soloLista = soloLista
        self.lingua = lingua
        global caratteriBianchi, caratteriNeri, caratteri, Lingua
        Lingua = lingua
        if lingua == 'Italiano':
            caratteriBianchi = 'PACTDR'
            caratteriNeri = 'PACTDR'
            caratteri = caratteriBianchi
        elif lingua == 'English':
            caratteriBianchi = 'PBNRQK'
            caratteriNeri = 'PBNRQK'
            caratteri = caratteriBianchi
        else:
            caratteriBianchi = '♙♗♘♖♕♔'
            caratteriNeri = '♟♝♞♜♛♚'
            caratteri = caratteriBianchi+caratteriNeri
        self.mode = mode
        if scacchiera == None: 
            self.scacchiera = Scacchiera(configurazionePersonalizzata)
        else:
            self.scacchiera = scacchiera
        self.turno = BIANCO
        self.mosse = []
        self.mosseAlgebriche = []
        self.tipiMosse = []
        self.mosseSenzaMangiare = 0
        self.tempiBianco = []
        self.tempiNero = []
        self.storiaConfigurazioni = [Scacchiera()]
        self.ultimaMossaIrreversibile = 0
        self.biancoArroccato = False
        self.neroArroccato = False
        self.mangiatiBianchi = []
        self.mangiatiNeri = []
        self.stampa = stampa
        self.biancoAI = biancoAI
        self.neroAI = neroAI
        self.esito = 'NESSUNO'
        self.inGioco = False
        
    def __str__(self):
        info = self.lingua + '\n\nPGN:\n'
        info += self.salvaPGN(soloReturn = True) + '\n\n'
        info += 'Scacchiera:' + str(self.scacchiera) + '\n\n'
        info += 'Tempo Bianco: ' + str(sum(self.tempiBianco)) + ' s\n\n'
        info += 'Tempo Nero:   ' + str(sum(self.tempiNero)) + ' s\n\n'
        if self.biancoArroccato: info += 'Il Bianco ha arroccato.\n\n'
        if self.neroArroccato: info += 'Il Nero ha arroccato.\n\n'
        punteggioB, punteggioN = self.scacchiera.getPunteggio()
        info += 'Conta punteggi pezzi: ' + str(punteggioB-punteggioN) + '\n\n'
        info += 'Esito: ' + self.esito
        return info
    
    def stampaStoria(self):
        for s in self.storiaConfigurazioni:
            s.stampa()
            
    def cambiaTurno(self):
        self.turno = NERO if self.turno == BIANCO else BIANCO
            
    def irreversibile(self, mossa, tipoMossa):
        mossaPedone = True if tipoMossa in ('Avanza1', 'Avanza2', 
                                            'Pedone Mangia', 'Enpassant', 
                                            'Promozione Avanza', 
                                            'Promozione Mangia') else False
        arrocco = True if tipoMossa[:7] == 'Arrocco' else False
        mangiato = True if tipoMossa in ('Mangia', 'Enpassant', 
                                         'Promozione Mangia') else False
        return mossaPedone or arrocco or mangiato
    
    def getMosseStandard(self):
        txt = ''
        for i in range(len(self.mosseAlgebriche)):
            mossa = self.mosseAlgebriche[i]
            if not i % 2: # Pari, mossa Bianco
                txt += str(i // 2 + 1) + '.' +' ' * (4 - len(str(i // 2 + 1)))
                txt += mossa + ' ' * (7 - len(mossa))
            else:
                txt += ' ' + mossa + '\n'
        return txt
                
    def getTempoTot(self, colore):
        if colore == BIANCO:
            return sum(self.tempiBianco)
        else:
            return sum(self.tempiNero)
        
    def esploraStorico(self):
        for i in range(len(self.mosse)):
            s = self.storiaConfigurazioni[i+1]
            mossa = self.mosse[i]
            mossaAlg = self.mosseAlgebriche[i]
            stop = input('Clicca invio per Proseguire, stop per concludere:  ')
            if stop == 'stop': break
            s.stampa()
            print(str((i//2)+1)+'. '+mossa+' ('+mossaAlg+')')
            
    def getPezzi(self):
        return self.scacchiera.getPezzi(self.turno)
                    
    def mossePossibili(self):
        pezzi = self.scacchiera.getPezzi(self.turno)
        mosse = []
        for pezzo in pezzi:
            mosse += pezzo.mossePossibili(self)
        return mosse        
            
    def checkStallo(self):
        if self.turno == BIANCO: 
            sottoScacco = self.scacchiera.checkScaccoBianco()  
        else:
            sottoScacco = self.scacchiera.checkScaccoNero()
        if not sottoScacco:
            mosse = self.mossePossibili()
            if len(mosse) == 0:
                self.esito = 'STALLO.'
                self.Result = '1/2-1/2'
                return True
        return False

    def checkPatta50Mosse(self):
        if self.mosseSenzaMangiare >= 50 :
            self.esito = 'PATTA per 50 mosse senza mangiare.'
            self.Result = '1/2-1/2'
            return True
        return False
    
    def checkRipetizione(self):
        count = 1
        inizio = self.ultimaMossaIrreversibile
        for i in range(inizio, len(self.storiaConfigurazioni)-1):
            config = self.storiaConfigurazioni[i]
            if configurazioniUguali(config, self.storiaConfigurazioni[-1]):
                turno = NERO if i%2 else BIANCO
                stessoTurno = self.turno == turno
                if stessoTurno:
                    count += 1
        if count >= 3:
            self.esito = 'PATTA per ripetizione.'
            self.Result = '1/2-1/2'
            return True
        return False
        
    def checkPatta(self):
        res = self.checkStallo() or self.checkPatta50Mosse()
        res = res or self.checkRipetizione()
        return  res
    
    def checkVinceBianco(self):
        if self.turno == NERO and self.scacchiera.checkScaccoNero():
            mosse = self.mossePossibili()
            if len(mosse) == 0:
                self.esito = 'Vince il BIANCO.'
                self.Result = '1-0'
                return True
        return False
    
    def checkVinceNero(self):
        if self.turno == BIANCO and self.scacchiera.checkScaccoBianco():
            mosse = self.mossePossibili()
            if len(mosse) == 0:
                self.esito = 'Vince il NERO.'
                self.Result = '0-1'
                return True
        return False
    
    def checkFine(self):
        if self.checkPatta():
            return True
        elif self.checkVinceBianco():
            return True
        elif self.checkVinceNero():
            return True
        return False
    
    def stampaRisultato(self):
        print('Esito: '+self.esito)
    
    def checkLegale(self, mossa):
        # Sintassi
        if len(mossa) in (4,5):
            pa, p1, qa, q1 = mossa[0:4]; p, q = (pa+p1, qa+q1)
            pezzo = self.scacchiera.getPezzo(p)
            mangiato = self.scacchiera.getPezzo(q)
            c1 = pa in lettere and qa in lettere 
            c1 = c1 and p1 in numeri and q1 in numeri
            if c1:
                if len(mossa) == 5:
                    promosso = mossa[4]
                    promovibili = caratteri[1:5]
                    if Lingua == 'Simboli': promovibili += caratteri[7:11]
                    if not (pezzo.nome == 'PEDONE' and promosso in promovibili):
                        return False, None
                # Selezionato un pezzo giusto
                if pezzo == None:
                    return False, None
                if pezzo.colore != self.turno:
                    return False, None
                # Mangiando sé stesso
                if mangiato != None and mangiato.colore == self.turno:
                    return False, None
                return pezzo.mossaLecita(self.scacchiera, mossa)
        return False, None
    
    def muovi(self, mossa):
        # Qui mossa sarà in formato ppaaP (partenza, arrivo, promozione)
        ok, tipoMossa = self.checkLegale(mossa)
        if ok:
            pezzo = self.scacchiera.getPezzo(mossa[:2])
            promozione = pezzo.nome == 'PEDONE'
            promozione = promozione and mossa[3] in ('1','8')
            if promozione and len(mossa) == 4:
                if self.mode == '2p' or (self.mode == '1p' and self.turno == BIANCO):
                    pezzi = '♕♖♘♗' if self.turno == BIANCO else '♛♜♞♝'
                    txt = 'In cosa vuoi promuovere?\n'
                    txt += 'Seleziona il numero corrispondente tra le opzioni.'
                    txt += '\n\t1 - ' + pezzi[0] + '\n\t2 - ' + pezzi[1]
                    txt += '\n\t3 - ' + pezzi[2] + '\n\t4 - ' + pezzi[3] 
                    txt += '\t->'
                    i = input(txt)
                    while not i in ('1', '2', '3', '4'):
                        self.scacchiera.stampa()
                        i = input(txt)
                    pezzi = caratteriBianchi if self.turno == BIANCO else caratteriNeri
                    finale = pezzi[-int(i) - 1]
                    mossa += finale
            eseguiMossa(self, mossa, tipoMossa)
            self.cambiaTurno()
            self.mosse.append(mossa)
            self.tipiMosse.append(tipoMossa)
            if tipoMossa in ('Mangia','Enpassant', 'Pedone Mangia', 
                             'Promozione Mangia'):
                self.mosseSenzaMangiare = 0
            else:
                self.mosseSenzaMangiare += 1
            if self.irreversibile(mossa, tipoMossa):
                self.ultimaMossaIrreversibile = len(self.storiaConfigurazioni)
            scacchieraPrima = self.storiaConfigurazioni[-1]
            scacchieraDopo = Scacchiera(self.scacchiera.pezzi)
            if len(self.mosse) == 118: # Debug
                pass
            mossaAlg = completa2algebrica(mossa, tipoMossa, scacchieraPrima, 
                                          scacchieraDopo)
            #if tipoMossa in ('Promozione Avanza','Promozione Mangia'): # Debug
                #print('ho promosso con '+mossa+' ('+mossaAlg+')')
            self.mosseAlgebriche.append(mossaAlg)
            self.storiaConfigurazioni.append(Scacchiera(self.scacchiera.pezzi))
        return ok
    
    def acquisisciMossa(self, listaMosse):
        colore = 'BIANCO' if self.turno == BIANCO else 'NERO'
        if len(listaMosse) > 0:
            if self.mode != '0p' and self.stampa:
                input('INVIO per andare alla mossa successiva_')
            mossa = listaMosse.pop()
            if mossa == 'back': return mossa
            indiceMossa = len(self.mosse)
            if tipoMossa(mossa) == 'Mossa Algebrica':
                mossa = algebrica2completa(mossa, self.scacchiera, 
                                           indiceMossa % 2)
            if len(listaMosse) == 0:
                if self.stampa:
                    print('Lista mosse esaurita')
                if self.soloLista: self.inGioco = False
        else:
            if self.mode == '2p':
                mossa = input('...Tocca al '+colore+': ')
            elif self.mode == '1p':
                if self.turno == NERO: mossa = self.neroAI(self)  
                else: mossa = input('...Tocca al '+colore+': ')
            elif self.mode == '0p':
                if self.turno == BIANCO: mossa = self.biancoAI(self)  
                else: mossa = self.neroAI(self)
        return mossa
    
    def gioca(self, listaMosse = []):
        global caratteriBianchi, caratteriNeri, caratteri, Lingua
        self.inGioco = True
        if self.lingua == 'Italiano':
            caratteriBianchi = 'PACTDR'
            caratteriNeri = 'PACTDR'
            caratteri = caratteriBianchi
        elif self.lingua == 'English':
            caratteriBianchi = 'PBNRQK'
            caratteriNeri = 'PBNRQK'
            caratteri = caratteriBianchi
        else:
            caratteriBianchi = '♙♗♘♖♕♔'
            caratteriNeri = '♟♝♞♜♛♚'
            caratteri = caratteriBianchi+caratteriNeri
        Lingua = self.lingua
        mossa = 'inizio'
        listaMosse.reverse()
        t = time.time()
        fine = False
        while self.inGioco and not fine:
            if self.stampa: self.scacchiera.stampa()
            fine = self.checkFine()
            if not fine:
                if self.stampa and self.scacchiera.sonoSottoScacco(self.turno):
                    print('\n\aSCACCO AL RE!')
                if len(listaMosse) > 0: mossaDaLista = True
                else: mossaDaLista = False
                mossa = self.acquisisciMossa(listaMosse)
                if mossa == 'back':
                    self.indietro()
                    if self.mode == '1p':
                        self.indietro()
                if mossa == 'stop':
                    self.inGioco = False
                else:
                    ok = self.muovi(mossa)
                    if ok:
                        deltaT = time.time() - t
                        t = time.time()
                        if self.turno == BIANCO:
                            self.tempiNero.append(deltaT)
                        else:
                            self.tempiBianco.append(deltaT)
                        pezzi = self.scacchiera.getPezzi(self.turno)
                        for pezzo in pezzi:
                            if pezzo.nome == 'PEDONE':
                                pezzo.appenaMossoDoppio = False
                    else:
                        if mossaDaLista:
                            self.inGioco = False
                            errore = 'Errore: le mosse date in input devono '
                            errore += 'essere legali: '+mossa+' non lo è.'
                            self.esito = 'Terminata per mossa illegale'
                            return errore
                        # Inizio debug
#                        turno = 'BIANCO' if self.turno == BIANCO else 'NERO'
#                        print('Turno del '+turno)
#                        self.scacchiera.stampa()
#                        print('Ha provato a fare una mossa illegale: '+mossa)
                        # Fine debug
                        if self.stampa: print('Mossa Illegale.')
            else:
                if self.esito in ('Vince il BIANCO.', 'Vince il NERO.'):
                    self.mosseAlgebriche[-1]+='+' #Scacco Matto Algebrico
        self.checkFine()
        if self.stampa: self.stampaRisultato()
        
    def indietro(self):
        global tIndietro, indietro
        indietro += 1
        t = time.time()
        if len(self.mosse) == 0:
            return
        turno = self.turno
        mossa = self.mosse.pop()
        self.mosseAlgebriche.pop()
        p, q = (mossa[:2], mossa[2:4])
        tipoMossa = self.tipiMosse.pop()
        if turno == BIANCO: 
            tempi = self.tempiNero
            mangiati = self.mangiatiBianchi
        else: 
            tempi = self.tempiBianco
            mangiati = self.mangiatiNeri
        tempi.pop()
        if self.ultimaMossaIrreversibile == len(self.storiaConfigurazioni):
            self.ultimaMossaIrreversibile -= 1
        pezzo = self.scacchiera.getPezzo(q)
        pezzo.storiaPosizioni.pop()
        sposta(self.scacchiera, q+p)
        pezzo.posizione = p
        if tipoMossa == 'Sposta':
            self.mosseSenzaMangiare -= 1
        elif tipoMossa == 'Mangia':
            mangiato = mangiati.pop()
            self.scacchiera.pezzi[mangiato.posizione] = mangiato
        elif tipoMossa == 'Avanza1':
            self.mosseSenzaMangiare -= 1
        elif tipoMossa == 'Avanza2':
            pezzo.appenaMossoDoppio = False
            self.mosseSenzaMangiare -= 1
        elif tipoMossa == 'Pedone Mangia':
            mangiato = mangiati.pop()
            self.scacchiera.pezzi[mangiato.posizione] = mangiato
        elif tipoMossa == 'Enpassant':
            mangiato = mangiati.pop()
            self.scacchiera.pezzi[mangiato.posizione] = mangiato
        elif tipoMossa == 'Promozione Avanza':
            self.scacchiera.pezzi[p] = Pedone(p,pezzo.colore,
                                             pezzo.storiaPosizioni)
        elif tipoMossa == 'Promozione Mangia':
            self.scacchiera.pezzi[p] = Pedone(p,pezzo.colore,
                                             pezzo.storiaPosizioni)
            mangiato = mangiati.pop()
            self.scacchiera.pezzi[mangiato.posizione] = mangiato
        elif tipoMossa == 'Arrocco Corto':
            if turno == NERO: torre = self.scacchiera.getPezzo('f1')  
            else: torre = self.scacchiera.getPezzo('f8')
            mossaTorre = 'f1h1' if turno == NERO else 'f8h8'
            sposta(self.scacchiera, mossaTorre)
            torre.storiaPosizioni.pop()
            torre.posizione = torre.storiaPosizioni[0]
            self.mosseSenzaMangiare -= 1
        elif tipoMossa == 'Arrocco Lungo':
            if turno == NERO: torre = self.scacchiera.getPezzo('d1') 
            else: torre = self.scacchiera.getPezzo('d8')
            mossaTorre = 'd1a1' if turno == NERO else 'd8a8'
            sposta(self.scacchiera, mossaTorre)
            torre.storiaPosizioni.pop()
            torre.posizione = torre.storiaPosizioni[0]
            self.mosseSenzaMangiare -= 1
        self.storiaConfigurazioni.pop()
        self.cambiaTurno()
        dt = time.time() - t
        tIndietro += dt
        
    def carica(nome):
        file = open(nome, "r")
        stringhe = file.readlines()
        for i in range(len(stringhe)):
            if stringhe[i] == 'Sequenza Mosse:\n':
                break
        stringhe = stringhe[i+2:]
        mosse = []; tipiMosse = [];
        tempiBianco = []; tempiNero = [];
        cifre = '0123456789'
        for s in stringhe:
            mossa = ''; tempo = ''; tipo = '';
            lettera = True; numero = False; cercaTempo = True
            for ch in s:
                # Cerca Mossa
                if len(mossa) < 4:
                    if lettera and ch in lettere:
                        mossa += ch
                        lettera = False; numero = True
                    elif numero and ch in numeri:
                        mossa += ch
                        lettera = True; numero = False
                    else:
                        mossa = ''
                # Cerca Tempo
                if cercaTempo:
                    if tempo == '' and ch in cifre:
                        tempo += ch
                    elif len(tempo) > 0:
                        if ch in cifre or ch == '.' or ch == ' ':
                            tempo += ch
                        elif ch == 's':
                            tempo = tempo[:-1]
                            cercaTempo = False
                        else:
                            tempo = ''
                # Cerca Tipo
                if tipo == '':
                    if ch == '(':
                        tipo += ch
                else:
                    tipo += ch
            if tipo != '':
                tipo = tipo[1:-2]
                tipiMosse.append(tipo)
            if mossa != '': mosse.append(mossa)
            if tempo != '':
                if len(tempiBianco) == len(tempiNero):
                    tempiBianco.append(float(tempo))
                else:
                    tempiNero.append(float(tempo))
        game = Partita(stampa = False)
        game.gioca(mosse)
        game.tempiBianco = tempiBianco
        game.tempiNero = tempiNero
        game.tipiMosse = tipiMosse
        return game
    
    def caricaPGN(nome):
        mosse, lingua = getMosseFromPGN(nome)
        info = getInfoFromPGN(nome)
        game = Partita(stampa = False, lingua = lingua, mode = '0p', soloLista = True)
        game.gioca(mosse)
        game.Event = info['Event'] if 'Event' in info else 'Amichevole'
        game.Site = info['Site'] if 'Site' in info else ''
        game.Date = info['Date'] if 'Date' in info else 'time.strftime("%Y.%m.%d")'
        game.Round = info['Round'] if 'Round' in info else '?'
        game.White = info['White'] if 'White' in info else 'Giocatore 1'
        game.Black = info['Black'] if 'Black' in info else 'Giocatore 2'
        game.Result = info['Result'] if 'Result' in info else '*'
        return game
    
    def salvaPGN(self, nome = 'partita', soloReturn = False):
        Event = '[Event "'+self.Event+'"]\n'
        Site = '[Site "'+self.Site+'"]\n'
        Date = '[Date "'+self.Date+'"]\n'
        Round = '[Round "'+self.Round+'"]\n'
        White = '[White "'+self.White+'"]\n'
        Black = '[Black "'+self.Black+'"]\n'
        Result = '[Result "'+self.Result+'"]\n'
        # Mosse
        listaMosse = []
        rigaMossa = ''
        for i in range(len(self.mosseAlgebriche)):
            numero = '' if i % 2 else ' '+str(i//2+1)+'.'
            parola = ' '+self.mosseAlgebriche[i]
            if len(rigaMossa)+len(numero) <= 80:
                rigaMossa += numero
                if len(rigaMossa)+len(parola) < 80:
                    rigaMossa += parola
                else:
                    listaMosse.append(rigaMossa[1:])
                    rigaMossa = parola
            else:
                listaMosse.append(rigaMossa[1:])
                rigaMossa = numero
                if len(rigaMossa)+len(parola) < 80:
                    rigaMossa += parola
                else:
                    listaMosse.append(rigaMossa[1:])
                    rigaMossa = parola
        listaMosse.append(rigaMossa[1:])
        Mosse = ''
        for rigaMossa in listaMosse:
            Mosse +='\n'+rigaMossa
        txt = Event + Site + Date + Round + White + Black + Result
        if len(listaMosse[-1]) + len(self.Result) < 80: spazio = ' '
        else: spazio = '\n'
        txt += Mosse + spazio + self.Result
        formato = '.pgn' if nome[-4:] != '.pgn' else ''
        if not soloReturn:
            file = open(nome+formato, 'w')
            file.write(txt)
            file.close()
        return txt
    
    def salvaCompleta(self, nome = 'partita.txt'):
        file = open(nome, "w")
        file.write(nome)
        file.write('\nmode: '+self.mode+'\n')
        for configurazione in self.storiaConfigurazioni:
            file.write(str(configurazione)+'\n')
        file.write('\nSequenza Mosse:\n\n')
        for i in range(len(self.mosse)):
            mossa = self.mosse[i]
            tipoMossa = self.tipiMosse[i]
            if not i % 2: autore, tempi = ('BIANCO', self.tempiBianco)  
            else: autore, tempi = ('NERO', self.tempiNero)
            txt = '\t'+str(i)+'.\t'+mossa+' giocata dal '+autore+'\tin '
            txt += str(int(tempi[i//2]*100000)/100000)+' s. ('+tipoMossa+')\n'
            file.write(txt)
        file.write('\nTotale Tempo impiegato dal BIANCO: ') 
        file.write(str(int(sum(self.tempiBianco)*100000)/100000) + ' s\n')
        file.write('Totale Tempo impiegato dal NERO:   ')
        file.write(str(int(sum(self.tempiNero)*100000)/100000) + ' s\n')
        file.write('\nesito: '+self.esito+'.')
        file.close()
            
# Funzioni ammissibilità mosse
        
# Funzioni Generali

def noSpeciali(scacchiera, mossa, chiAttacca):
    pa, p1, qa, q1 = mossa; p, q = pa+p1, qa+q1;
    pezzo = scacchiera.getPezzo(p)
    turno = pezzo.colore
    mangiato = scacchiera.getPezzo(q)
    if chiAttacca(scacchiera, pezzo, q): 
        sposta(scacchiera, mossa)
        if not q in scacchiera.pezzi: # Debug
            scacchiera.stampa()
            print(mossa)
        scacchiera.pezzi[q].posizione = q
        sottoScacco = scacchiera.sonoSottoScacco(turno)
        scacchiera.pezzi[q].posizione = p
        sposta(scacchiera, q+p)
        tipo = 'Sposta'
        if mangiato != None:
            tipo = 'Mangia'
            scacchiera.pezzi[q] = mangiato
        if not sottoScacco:
            return True, tipo
    return False, None
    
# Funzioni Specifiche   
    
def mlCavallo(scacchiera, mossa):
    return noSpeciali(scacchiera, mossa, cavalloAttacca)

def mlAlfiere(scacchiera, mossa):
    return noSpeciali(scacchiera, mossa, alfiereAttacca)

def mlTorre(scacchiera, mossa):
    return noSpeciali(scacchiera, mossa, torreAttacca)

def mlRegina(scacchiera, mossa):
    return noSpeciali(scacchiera, mossa, reginaAttacca)

def mlPedone(scacchiera, mossa):
    pa, p1, qa, q1 = mossa[0:4]; p, q = pa+p1, qa+q1;
    if dist(p, q) > 2:
        return False, None
    pezzo = scacchiera.getPezzo(p) # So che è un pedone
    turno = pezzo.colore
    mangiato = scacchiera.getPezzo(q)
    avanza = up if pezzo.colore == BIANCO else down
    if avanza(p) != None:
        # Provo ad Avanzare
        mosso = pezzo.mosso()
        avanza2Par = mosso == False and scacchiera.getPezzo(avanza(p)) == None
        if avanza(p) == q or (avanza(avanza(p)) == q and avanza2Par): 
            if mangiato == None:
                sposta(scacchiera, mossa)
                sottoScacco = scacchiera.sonoSottoScacco(turno)
                sposta(scacchiera, q+p)
                if not sottoScacco:
                    tipo = 'Avanza1' if avanza(p) == q else 'Avanza2'
                    if q1 in ('1','8'): 
                        tipo = 'Promozione Avanza'
                    return True, tipo
        lato = right if right(p) != None and qa == right(p)[0] else False
        if not lato: 
            lato = left if left(p) != None and qa == left(p)[0] else False
        if lato:
            # Provo a mangiare
            if lato(avanza(p)) == q: 
                # Provo a mangiare Normale
                if mangiato != None: 
                    sposta(scacchiera, mossa)
                    sottoScacco = scacchiera.sonoSottoScacco(turno)
                    sposta(scacchiera, q+p)
                    scacchiera.pezzi[q] = mangiato
                    if not sottoScacco:
                        if q1 in ('1','8'):
                            tipo = 'Promozione Mangia'  
                        else: tipo = 'Pedone Mangia'
                        return True, tipo
                else:
                    mangiatoEnpassant = scacchiera.getPezzo(lato(p))
                    # Provo a mangiare Enpassant
                    if mangiatoEnpassant != None: 
                        cApp = mangiatoEnpassant.nome == 'PEDONE'
                        c = cApp and mangiatoEnpassant.colore != pezzo.colore
                        if c: 
                            if mangiatoEnpassant.appenaMossoDoppio == True:
                                sposta(scacchiera, mossa)
                                del scacchiera.pezzi[lato(p)]
                                sottoScacco = scacchiera.sonoSottoScacco(turno)
                                sposta(scacchiera, q+p)
                                scacchiera.pezzi[lato(p)] = mangiatoEnpassant
                                if not sottoScacco:
                                    return True, 'Enpassant'
    return False, None

def mlRe(scacchiera, mossa):
    pa, p1, qa, q1 = mossa; p = pa+p1;
    re = scacchiera.getPezzo(p)
    turno = re.colore
    # Provo Mossa Normale
    ok, tipoMossa = noSpeciali(scacchiera, mossa, reAttacca)
    if ok:
        return True, tipoMossa
    # Provo ad arroccare
    i = '1' if re.colore == BIANCO else '8' # Riga dell'arrocco
    if mossa == 'e'+i+'c'+i or mossa == 'e'+i+'g'+i:
        torre = scacchiera.getPezzo('a'+i) # Arrocco Lungo
        if mossa == 'e'+i+'g'+i: 
            torre = scacchiera.getPezzo('h'+i) # Arrocco Corto
        c1 = torre != None and torre.colore == re.colore 
        c1 = c1 and torre.nome == 'TORRE'
        if c1:
            c2 = not torre.mosso() and not re.mosso()
            if c2:
                if mossa == 'e'+i+'c'+i: # Arrocco Lungo:
                    c3 = scacchiera.getPezzo('b'+i) == None
                    c3 = scacchiera.getPezzo('c'+i) == None and c3
                    c3 = scacchiera.getPezzo('d'+i) == None and c3
                else: # Arrocco Corto:
                    c3 = scacchiera.getPezzo('f'+i) == None
                    c3 = scacchiera.getPezzo('g'+i) == None and c3
                if c3:
                    c4 = not scacchiera.sonoSottoScacco(turno)
                    if c4:
                        c5 = True
                        pezzi = scacchiera.getPezzi(1-re.colore)
                        posizioni = ['d'+i, 'c'+i] # Arrocco Lungo
                        if mossa == 'e'+i+'g'+i: 
                            posizioni = ['f'+i, 'g'+i] # Arrocco corto
                        for pezzo in pezzi:
                            cApp = pezzo.attacca(scacchiera, posizioni[0])
                            c = cApp or pezzo.attacca(scacchiera, posizioni[1])
                            if c:
                                c5 = False; break;
                        if c5:
                            if mossa == 'e'+i+'g'+i: tipo = 'Arrocco Corto' 
                            else: tipo = 'Arrocco Lungo'
                            return True, tipo
    return False, None
    
# Altre funzioni

def sposta(scacchiera, mossa):
    p, q = (mossa[:2], mossa[2:4])
    pezzo = scacchiera.getPezzo(p)
    scacchiera.pezzi[q] = pezzo
    del scacchiera.pezzi[p]
        
def eseguiMossa(partita, mossa, tipoMossa):
    p, q = mossa[:2], mossa[2:4]
    s = partita.scacchiera
    pezzo = s.getPezzo(p)
    mangiato = s.getPezzo(q)
    if tipoMossa == 'Sposta':
        pass
    elif tipoMossa == 'Mangia':
        pass
    elif tipoMossa == 'Avanza1':
        pass
    elif tipoMossa == 'Avanza2':
        pezzo.appenaMossoDoppio = True # Controlla quando lo si rifalsifica
    elif tipoMossa == 'Pedone Mangia':
        pass
    elif tipoMossa in ('Promozione Avanza', 'Promozione Mangia'):
        colore = NERO if q[1] == '1' else BIANCO
        promosso = mossa[4] if len(mossa) == 5 else ' '
        if colore == BIANCO:
            regina = promosso in (caratteriBianchi[4], ' ')
            torre = promosso == caratteriBianchi[3]
            cavallo = promosso == caratteriBianchi[2]
            alfiere = promosso == caratteriBianchi[1]
        else:
            regina = promosso in (caratteriNeri[4], ' ')
            torre = promosso == caratteriNeri[3]
            cavallo = promosso == caratteriNeri[2]
            alfiere = promosso == caratteriNeri[1]
        if regina:
            s.pezzi[p] = Regina(q, colore, pezzo.storiaPosizioni)
        elif torre:
            s.pezzi[p] = Torre(q, colore, pezzo.storiaPosizioni)
        elif cavallo:
            s.pezzi[p] = Cavallo(q, colore, pezzo.storiaPosizioni)
        elif alfiere:
            s.pezzi[p] = Alfiere(q, colore, pezzo.storiaPosizioni)
    elif tipoMossa == 'Enpassant':
        mangiato = s.getPezzo(q[0]+p[1])
    elif tipoMossa == 'Arrocco Corto':
        if pezzo.colore == BIANCO:
            i = '1'
            partita.biancoArroccato = True
        else:
            i = '8'
            partita.neroArroccato = True
        sposta(s, 'h'+i+'f'+i)
        torre = s.getPezzo('f'+i)
        torre.storiaPosizioni.append('f'+i)
        torre.posizione = 'f'+i
    elif tipoMossa == 'Arrocco Lungo':
        if pezzo.colore == BIANCO:
            i = '1'
            partita.biancoArroccato = True
        else:
            i = '8'
            partita.neroArroccato = True
        sposta(s, 'a'+i+'d'+i)
        torre = s.getPezzo('d'+i)
        torre.storiaPosizioni.append('d'+i)
        torre.posizione = 'd'+i
    if mangiato != None:
        del partita.scacchiera.pezzi[mangiato.posizione]
    sposta(s, mossa)
    pezzo.posizione = q
    if mangiato != None:
        if mangiato.colore == BIANCO: partita.mangiatiBianchi.append(mangiato)
        if mangiato.colore == NERO: partita.mangiatiNeri.append(mangiato)
    pezzo.storiaPosizioni.append(q)

def configurazioniUguali(c1, c2):
    for a in lettere:
        for i in numeri:
            p = a+i
            pezzo1 = c1.getPezzo(p); pezzo2 = c2.getPezzo(p);
            if not pezzo1 == pezzo2:
                return False
            elif not pezzo1 == None:
                if pezzo1.nome == 'RE' or pezzo1.nome == 'TORRE':
                    if not pezzo1.mosso() == pezzo2.mosso():
                        return False
                # Controlla possibiltà di enpassant
    return True
    
def randomAI(partita):
    mosse = partita.mossePossibili()
    #mosse.append('back')
    n = len(mosse)
    if n == 0:
        return 'stop'
    i = rn.randint(0,n-1)
    return mosse[i]

def makeStats(nome = 'stats.txt', games = [], biancoAI = lambda p: randomAI(p), 
              neroAI = lambda p: randomAI(p), n = 1000, 
              stampaScacchiera = False):
    t = time.time()
    Finali = []
    contaMosse = {}
    for tipo in tipiMosse:
        contaMosse[tipo] = 0
    esiti = {'STALLO.':0, 'PATTA per 50 mosse senza mangiare.':0, 
             'PATTA per ripetizione.':0, 'Vince il BIANCO.':0, 
             'Vince il NERO.':0, 'NESSUNO':0}
    n = n if len(games) == 0 else len(games)
    for i in tqdm(range(n)):
        if len(games) == 0:
            game = Partita(mode = '0p', stampa = False, biancoAI = biancoAI, 
                           neroAI = neroAI)
            game.gioca()
        else:
            game = games[i]
        tempo = game.getTempoTot(BIANCO) + game.getTempoTot(NERO)
        Finali.append({'Scacchiera': game.storiaConfigurazioni[-1], 
                       'Esito': game.esito,
                       'Mosse': len(game.mosse),
                       'Tempo': tempo})
        for tipoMossa in game.tipiMosse:
            contaMosse[tipoMossa] += 1
        esiti[game.esito] += 1
    file = open(nome, "w")
    file.write(nome+'\n')
    for finale in Finali:
        esito = str(finale['Esito'])
        mosse = str(finale['Mosse'])
        tempo = str(int(finale['Tempo']*1000)/1000)
        txt = str(finale['Scacchiera'])+'\t\t' if stampaScacchiera else '\n'
        txt += esito + ' ' * (40 - len(esito))
        txt += mosse + ' ' * (5 - len(mosse)) + ' mosse,    '
        txt += tempo + ' ' * (9 - len(tempo)) + ' s'
        file.write(txt)
    file.write('\n\nOccorrenze tipologie di mosse.\n')
    for tipoMossa in contaMosse:
        file.write('\n\t'+tipoMossa+':'+(' '*(20-len(tipoMossa))))
        file.write(str(contaMosse[tipoMossa])+' volte')
    file.write('\n\tIndietro:            '+str(indietro)+' volte')
    file.write('\n\nOccorrenze esiti.\n')
    for esito in esiti:
        file.write('\n\t'+esito+':'+(' '*(40-len(esito))))
        file.write(str(esiti[esito])+' volte')
    dt = time.time() - t
    file.write('\n\nTempi.\n')
    file.write('\n\tCopia:             ' + str(tCopia) + ' s')
    file.write('\n\tInit Scacchiera:   ' + str(tInitScacchiera) + ' s')
    file.write('\n\tIndietro:          ' + str(tIndietro) + ' s')
    file.write('\n\tTotale:            ' + str(dt) + ' s')
    file.write('\n\nMedia Velocità:        '+str(int((n/dt)*100)/100)+' it/s')
    file.close()
    
###############################################################################
#                                                                             #
#    Taduzione delle notazioni usate per codificare le mosse                  #
#                                                                             #
###############################################################################

def completa2algebrica(mossa, tipoMossa, scacchieraPrima, scacchieraDopo):
    pa, p1, qa, q1 = mossa[0:4]; p = pa+p1; q = qa+q1;
    pezzo = scacchieraPrima.getPezzo(p)
    mangiato = scacchieraPrima.getPezzo(q)
    turno = pezzo.colore
    soggetto = pezzo.carattere
    azione = ''
    finale = ''
    oggetto = q
    if tipoMossa == 'Sposta':
        pass
    elif tipoMossa == 'Mangia':
        pass
    elif tipoMossa == 'Avanza1':
        pass
    elif tipoMossa == 'Avanza2':
        pass
    elif tipoMossa == 'Pedone Mangia':
        pass
    elif tipoMossa == 'Enpassant':
        mangiato = scacchieraPrima.getPezzo(qa+p1)
    elif tipoMossa == 'Arrocco Corto':
        return 'O-O'
    elif tipoMossa == 'Arrocco Lungo':
        return 'O-O-O'
    elif tipoMossa in ('Promozione Mangia', 'Promozione Avanza'):
        finale = '='
        promosso = mossa[4] if len(mossa) == 5 else ' '
        if turno == BIANCO:
            if promosso in (caratteriBianchi[4], ' '): indice = 4 
            elif promosso == caratteriBianchi[3]: indice = 3
            elif promosso == caratteriBianchi[2]: indice = 2
            elif promosso == caratteriBianchi[1]: indice = 1
            else:
                print('Errore con: \nPromosso = '+promosso+'\nTurno = '+str(turno))
                indice = 'Errore'
            finale += caratteriBianchi[indice]
        else:
            if promosso in (caratteriNeri[4], ' '): indice = 4 
            elif promosso == caratteriNeri[3]: indice = 3
            elif promosso == caratteriNeri[2]: indice = 2
            elif promosso == caratteriNeri[1]: indice = 1
            else:
                print('Errore con: \nPromosso = '+promosso+'\nTurno = '+str(turno))
                indice = 'Errore'
            finale += caratteriNeri[indice]
        # Sarebbe meglio partita.caratteri ma non ho accesso alla partita in 
        # questa funzione
    finale += '+' if scacchieraDopo.checkScacco(1-turno) else ''
    if mangiato != None:
        azione = 'x'
    pezzi = scacchieraPrima.getPezzi(turno)
    ambigui = []
    for pezzoBis in pezzi:
        if pezzoBis.posizione != p:
            if pezzoBis.nome == pezzo.nome:
                ok, tipo = pezzoBis.mossaLecita(scacchieraPrima, 
                                                pezzoBis.posizione+q)
                if ok:
                    ambigui.append(pezzoBis)
    if len(ambigui) > 0:
        colonneDiverse = True
        righeDiverse = True
        for ambiguo in ambigui:
            if ambiguo.posizione[0] == pa:
                colonneDiverse = False
            if ambiguo.posizione[1] == p1:
                righeDiverse = False
        if colonneDiverse:
            soggetto += pa
        else:
            if righeDiverse:
                soggetto += p1
            else:
                soggetto += p
    return soggetto + azione + oggetto + finale

def cercaArrivo(mossaAlg):
    q = ''
    x = mossaAlg[::-1] # sarebbe la stringa letta al contrario
    for ch in x:
        if len(q) == 2: return q
        elif len(q) == 1:
            if ch in lettere: return ch+q
            else:
                q = ''
        elif len(q) == 0:
            if ch in numeri:
                q = ch
                
def cercaSpecifiche(mossaAlg):
    q = cercaArrivo(mossaAlg)
    if q == None:
        print(mossaAlg)
    qCorr = q
    i=-2
    for ch in mossaAlg:
        if qCorr == '':
            break
        else:
            if ch == qCorr[0]:
                qCorr = qCorr[1:]
            else:
                if ch != q[0]:
                    qCorr = q
        i += 1
    x = mossaAlg[1:i]
    if x == '':
        return ''
    if x[-1] == 'x':
        return x[:-1]
    return x
                
def algebrica2completa(mossaAlg, scacchiera, turno):
    finale = ''
    if '=' in mossaAlg:
        aggiorna = False
        for ch in mossaAlg:
            if aggiorna:
                finale = ch
                break
            if ch == '=': aggiorna = True
    global errori
    if 'O-O' in mossaAlg: # Arrocco
        riga = '1' if turno == BIANCO else '8'
        if 'O-O-O' in mossaAlg: #Arrocco Lungo
            return 'e'+riga+'c'+riga
        if 'O-O' in mossaAlg: #Arrocco corto
            return 'e'+riga+'g'+riga
    # Controlla l'esattezza di turno
    car = mossaAlg[0] # se è un pedone non è detto
    #turno = BIANCO if car in caratteriBianchi else NERO 
    q = cercaArrivo(mossaAlg)
    specifiche = cercaSpecifiche(mossaAlg)
    pezzi = scacchiera.getPezzi(turno)
    p = None
    pezziPapabili = []
    for pezzo in pezzi: # if pezzo.colore == truno
        if pezzo.carattere == car:
            mossa = pezzo.posizione+q
            ok, tipo = pezzo.mossaLecita(scacchiera, mossa)
            if ok:
                if len(specifiche) == 0: 
                    p = pezzo.posizione
                    pezziPapabili.append(pezzo)
                elif len(specifiche) == 1:
                    if specifiche in lettere:
                        if pezzo.posizione[0] == specifiche: 
                            p = pezzo.posizione
                            pezziPapabili.append(pezzo)
                    elif specifiche in numeri:
                        if pezzo.posizione[1] == specifiche: 
                            p = pezzo.posizione
                            pezziPapabili.append(pezzo)
                elif len(specifiche) == 2:
                    if pezzo.posizione == specifiche: 
                        p = pezzo.posizione
                        pezziPapabili.append(pezzo)
    if p != None:
        if p==q: # Debug
            print('Mossa Algebrica: '+mossaAlg)
            print('Mossa Completa:  '+p+q)
        return p+q+finale
    else:
        scacchiera.stampa()
        print('La mossa tentata è '+mossaAlg)
        print('Specifiche: \''+specifiche+'\'')
        print('Pezzi trovati:')
        for pezzo in pezzi:
            print(pezzo.carattere+'('+str(pezzo)+') in '+pezzo.posizione)
        print('Pezzi Papabili:')
        for papabile in pezziPapabili:
            print(str(papabile)+' in '+papabile.posizione)
        #errori.append((Scacchiera(scacchiera.pezzi),mossaAlg))
        return 'Non ho trovato il pezzo da muovere'

def trasformaMosse(mosse, lingua = None):
    # La lingua non è né la lingua di partenza né la lingua di arrivo,
    # bensì la lingua con cui è noto essera la notazione delle mosse in 
    # entrata (precondizione) E la lingua con cui sarà la notazione delle
    # mosse in uscita.
    alg2comp = tipoMossa(mosse[0]) == 'Mossa Algebrica'
    mosseCopia = mosse.copy()
    if lingua == None:
        lingua = 'Simboli'
        if alg2comp:
            lingua = getLingua(mosse)
    game = Partita(mode = '0p', stampa = False, lingua = lingua)
    game.gioca(mosseCopia)
    return game.mosse.copy() if alg2comp else game.mosseAlgebriche.copy()

def tipoMossa(mossa):
    if len(mossa) in (4,5):
        pa, p1, qa, q1 = mossa[0:4]
        c1 = pa in lettere and qa in lettere 
        c1 = c1 and p1 in numeri and q1 in numeri
        if c1:
            if len(mossa) == 4:
                return 'Mossa Completa'
            if len(mossa) == 5:
                promosso = mossa[4]
                promovibili = caratteri[1:5]
                if Lingua == 'Simboli': promovibili += caratteri[7:11]
                if promosso in promovibili:
                    return 'Mossa Completa'
    return 'Mossa Algebrica'

def getLingua(mosse):
    pItaliano = 0; pEnglish = 0; pSimboli = 0;    
    if tipoMossa(mosse[0]) == 'Mossa Algebrica':
        for mossa in mosse:
            if mossa[0] in italiano: pItaliano += 1
            if mossa[0] in english: pEnglish += 1
            if mossa[0] in simboli: pSimboli += 1
    else:
        for mossa in mosse:
            if len(mossa) == 5:
                if mossa[4] in italiano: pItaliano += 1
                if mossa[4] in english: pEnglish += 1
                if mossa[4] in simboli: pSimboli += 1
    probabilita = (pItaliano, pEnglish, pSimboli)
    if sum(probabilita) == 0: return 'English'
    elif pItaliano == max(probabilita): return 'Italiano'
    elif pEnglish == max(probabilita): return 'English'
    elif pSimboli == max(probabilita): return 'Simboli'
    
def getInfoFromPGN(nome):
    formato = '.pgn' if nome[-4:] != '.pgn' else ''
    file = open(nome+formato,'r')
    lines = file.readlines()
    info = {}
    for line in lines:
        if len(line)>8 and line[:8] == '[Event "':
            info['Event'] = line[8:-3]
        elif len(line)>7 and line[:7] == '[Site "':
            info['Site'] = line[7:-3]
        elif len(line)>7 and line[:7] == '[Date "':
            info['Date'] = line[7:-3]
        elif len(line)>8 and line[:8] == '[Round "':
            info['Round'] = line[8:-3]
        elif len(line)>8 and line[:8] == '[White "':
            info['White'] = line[8:-3]
        elif len(line)>8 and line[:8] == '[Black "':
            info['Black'] = line[8:-3]
        elif len(line)>9 and line[:9] == '[Result "':
            info['Result'] = line[9:-3]
    return info
    
def getMosseFromPGN(nome):
    formato = '.pgn' if nome[-4:] != '.pgn' else ''
    file = open(nome+formato,'r')
    lines = file.readlines()
    txt = ''
    ok = False
    for line in lines:
        if not ok and line[0] == '1': ok = True
        if ok: txt += line
    txt = txt.split()
    pItaliano = 0; pEnglish = 0; pSimboli = 0;
    mosse1 = []
    for parola in txt:
        if len(parola)>0:
            if not '.' in parola: # Non conto l'indice di mosse
                if not parola in risultati: # Non conto i risultati
                    mosse1.append(parola)
                    if parola[0] in italiano: pItaliano += 1
                    if parola[0] in english: pEnglish += 1
                    if parola[0] in simboli: pSimboli += 1
    probabilita = (pItaliano, pEnglish, pSimboli)
    if pItaliano == max(probabilita):
        lingua = 'Italiano'; insieme = italiano;
    elif pEnglish == max(probabilita):
        lingua = 'English'; insieme = english;
    elif pSimboli == max(probabilita):
        lingua = 'Simboli'; insieme = simboli;
    mosse = []
    for mossa in mosse1:
        if isMossaAlg(mossa):
            if not mossa[0] in insieme and not 'O-O' in mossa:
                prefisso = insieme[0]
                if lingua == 'Simboli' and len(mosse) % 2: # Turno == Nero
                    prefisso = insieme[6]
                mossa = prefisso+mossa
            mosse.append(mossa)
    return mosse, lingua

def isMossaAlg(mossa):
    # Non è esatta; distigue solo tra quello che potrebbe essere una mossa
    # algebrica e quello che sicuramente non lo è. Tornare True è condizione
    # necessaria (non sufficiente) affinché si tratti di una mossa Algebrica.
    if 'O-O' in mossa:
        return True
    q = cercaArrivo(mossa)
    if q == None: return False
    assenti = '\|"£$%&[]{}'
    for ch in assenti:
        if ch in mossa:return False
    return True

###############################################################################
#                                                                             #
#   Sezione dedicata a calcolo e visualizzazione delle distanze dei pezzi     #
#                                                                             #
###############################################################################
    
def distanza(pezzo, casella):
    if pezzo.posizione == casella:
        return 0
    s = Scacchiera({pezzo.posizione:pezzo}) 
    Tipo = type(pezzo)
    mosse = set([pezzo.posizione+pezzo.posizione])
    controllati = set()
    ok = False; c = True; d = 0
    while not ok and c:
        mosse2 = set()
        c = False
        for mossa in mosse:
            p = mossa[2:4]
            if not p in controllati:
                pezzo = Tipo(p)
                s = Scacchiera({p:pezzo})
                for a in lettere:
                    for i in numeri:
                        if pezzo.attaccaCheck(s, pezzo, a+i):
                            if not a+i in controllati:
                                mosse2.add(pezzo.posizione+a+i)
                if pezzo.posizione+casella in mosse2:
                    ok = True
                controllati.add(p)
                c = True
        mosse = mosse2
        d += 1
    return d if c else np.inf

def visualizzaMetrica(pezzo, salva = False):
    M = np.ones((8,8))
    for i in range(8):
        for j in range(8):
            p = lettere[j]+numeri[i]
            M[7-i,j] = distanza(pezzo, p)
    colorMap = mpl.cm.cool
    fig, ax = plt.subplots()
    im = ax.imshow(M, cmap=colorMap)
    titolo = 'Distanze per mosse necessarie\n'
    titolo += pezzo.nome + ' in ' + pezzo.posizione
    ax.set_title(titolo)
    plt.colorbar(im)
    if salva:
        plt.savefig('distanze_'+pezzo.nome+'_'+pezzo.posizione+'.png')
    return M
            
###############################################################################
#                                                                             #
#   Codici utilizzati in passato per testing                                  #
#                                                                             #
############################################################################### 

tTot = time.time()

#makeStats('provaStatistiche.txt', n = 100)

''' ESEMPIO 0p '''
#game = Partita(mode = '0p', stampa = False, lingua = 'Italiano')
#game.gioca()
#print(game)
#print(game.getMosseStandard())

''' ESEMPIO 1p '''
#game = Partita(mode = '1p')
#game.gioca()

''' ESEMPIO 2p '''
#game = Partita(mode = '2p')
#game.gioca()

''' ESEMPIO listaMosse '''
#game = Partita(mode = '2p')
#game.gioca(['QFIJEQBNF'])
#mosse = trasformaMosse(game.mosseAlgebriche)
#print(game.getMosseStandard())
#game.mossePossibili()

''' ESEMPIO listaMosseAlgebriche '''
#game = Partita(mode = '2p')
#game.gioca(['♘h3','♟a5','♙c4','♟c5','♘g5','♟h5','♘c3','♟f5','♕a4','♟b6','♘ge4',
#            '♞f6','♕d1','♞g8','♕c2','♝a6','♕b1','♟e6','♙e3','♜a7','♘f6+','♟xf6',
#            '♙e4','♟xe4','♘d5','♟e3','♕d3','♟xd2+','♗xd2','♛c7','♘e3','♝c8',
#            '♕e2','♝h6','♕d1','♚f8','♕g4','♟xg4','♙g3','♟a4','♔e2','♛f4','♗g2',
#            '♟e5','♖hd1','♛xc4+','♔e1','♛f7','♗c1','♛g7','♙f4','♞a6','♘f1',
#            '♛g6','♔d2','♛d3+','♔e1','♛xd1+','♔xd1','♞c7','♗c6','♟b5','♗f3',
#            '♚e7','♙a3','♚f7','♗c6','♜a8','♗e3','♚g6','♗d4','♞d5','♗xb5',
#            '♞de7','♙xe5','♚h7','♗a6','♟xd4','♗b7','♞d5','♙xf6','♞b6','♗e4++'])
#game.esploraStorico()
    
#c = Cavallo('b1')
#d = distanza(c, 'b1')
#print(d)

#a = Alfiere('c1')
#dd = distanza(a, 'e2')
#print(dd)
    
#c = Cavallo('c2')
#t = Torre('c2')
#a = Alfiere('c2')
#r = Re('c2')
#reg = Regina('c2')
#p = Pedone('c2')
#pezzi = [c,t,a,r,reg, p] 
#for pezzo in pezzi:
#    visualizzaMetrica(pezzo)
    
#game = Partita(mode = '0p')
#game.gioca()
#game.salvaCompleta('partitaRandom4.txt')

#for i in tqdm(range(25)):
#    game = Partita(mode = '0p', stampa = False)
#    game.gioca()

#game = Partita.carica('partitaRandom4.txt')

###############################################################################
#                                                                             #
#   Testing per traduzione mosse                                              #
#                                                                             #
############################################################################### 

###############################################################################
#games = []
#for i in tqdm(range(1,1999)):
#    game = Partita.caricaPGN('Dataset/Partita'+str(i))
#    if game.esito != 'NESSUNO':
#        games.append(game)
#makeStats('checkVittoria.txt', games = games)
#oks = []; errori = []; erroriAlg = [];
#arrocchi = 0
##file = open('provaTraduzioni.pgn', 'a')
#for game in tqdm(games):
#    #file.write(game.salvaPGN()+'\n\n')
#    tipi = game.tipiMosse
#    mosse1 = game.mosse
#    mosseAlgebriche1 = game.mosseAlgebriche
#    mosse2 = trasformaMosse(mosseAlgebriche1)
#    for mossa2 in mosse2:
#        if mossa2 == 'Non ho trovato il pezzo da muovere':
#            break
#    mosseAlgebriche2 = trasformaMosse(mosse1, lingua = 'English')
#    if len(mosse1) != len(mosse2):
#        print('Problema riga 1581.')
#    ok = len(mosse1)
#    for j in range(len(mosse1)):
#        if mosse1[j] != mosse2[j]:
#            ok -= 0.5
#            errori.append(mosse1[j]+' ≠ '+mosse2[j]+' ('+tipi[j]+')')
#        c0 = mosseAlgebriche1[j][-1] == '+'
#        c1 = mosseAlgebriche1[j] == mosseAlgebriche2[j]
#        # Con c2 escludo i probelmi di notare uno scacco matto
#        c2 = c0 and mosseAlgebriche1[j] + '+' == mosseAlgebriche2[j]
#        if not (c1 or c2):
#            ok -= 0.5
#            errore = mosseAlgebriche1[j]+' ≠ '+mosseAlgebriche2[j]
#            errore += ' ('+tipi[j]+')'
#            erroriAlg.append(errore)
#        if tipi[j] in ('Arrocco Corto', 'Arrocco Lungo'):
#            arrocchi += 1
#    ok /= len(mosse1)
#    oks.append(ok)
#file.close()
# Il codice in questo blocco non dà errore
###############################################################################

#game = Partita(mode = '0p', stampa = False, lingua = 'English')
#game.gioca()
#game.salvaPGN('provaLingue1')
#game1 = Partita.caricaPGN('provaLingue1')
#game1.salvaPGN('provaLingue2')

#game1 = Partita.caricaPGN('robinLiChess')
#game1.salvaPGN('robinLiChessRiprodotta')
    
tTot = time.time() - tTot
print('\n...Esecuzione in '+str(int(tTot*1000)/1000) + ' secondi.')    
    
###############################################################################
#                                                                             #
#   Commenti per idee e memo                                                  #
#                                                                             #
############################################################################### 
#
# Risolto problema di traduzione.
#
# Scrivi i setCampo e i getCampo
#
# CONTROLLA 'indietro' in modalità 1p quando annulli una promozione
#
# CONTROLLA ambiguità di notazione algebrica per promozione e scacco matto.
#
# CONTROLLA che funzioni / metodi scritti PRIMA dell'implementazione in cui si
# introducono più lingue funzionino anche dopo tale implementazione.
# 
# AGGIUNGI metodo Partita.stampa()
#
# Forse il metodo indietro potrebbe sfruttare più il salvataggio di 
# storiaConfigurazoni.
#
# Pareggi:
#   Differenziare tra pareggio proposto e obbligato
#   Pareggio per ripetizione:
#       controlla possibilità di enpassant
#