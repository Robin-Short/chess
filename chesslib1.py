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
from matplotlib.pyplot import imshow

modalita = ['0p', '1p', '2p', 'listaMosse']
backGround = '\u001b[46m' 
reset = '\u001b[0m'       

#Black: \u001b[30m
#Red: \u001b[31m
#Green: \u001b[32m
#Yellow: \u001b[33m
#Blue: \u001b[34m
#Magenta: \u001b[35m
#Cyan: \u001b[36m
#White: \u001b[37m
#Reset: \u001b[0m
#Background Black: \u001b[40m
#Background Red: \u001b[41m
#Background Green: \u001b[42m
#Background Yellow: \u001b[43m
#Background Blue: \u001b[44m
#Background Magenta: \u001b[45m
#Background Cyan: \u001b[46m
#Background White: \u001b[47m

tTot = 0
tCopia = 0              #~50%
tInitScacchiera = 0     # Non disgiunto dal precedente

BIANCO = 0
NERO = 1

#Tipi di mosse per effetto
MOSSA = 0
MANGIA = 1
ENPASSANT = 2
ARROCCO = 3
PROMOZIONE = 4

###############################################################################
#                                                                             #
#   Funzioni generiche utili                                                  #  
#                                                                             #
###############################################################################

def letters2ind(a):
    d = {'a':1,'b':2,'c':3,'d':4,'e':5,'f':6,'g':7,'h':8}
    return d[a]

def dist(p, q): # Distanza Manhattan
    return abs(letters2ind(p[0]) - letters2ind(q[0])) + abs(int(p[1]) - int(q[1]))

###############################################################################
#                                                                             #
#   Pezzo: Classe, metodi e funzioni                                          #
#                                                                             #
###############################################################################

class Pezzo():
    def __init__(self, pos, col, punt, nome, car, attaccaCheck = lambda pos: False, mossaLecita = lambda pos: True):
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
                self.storiaPosizioni)
        tCopia += time.time() - t
        return x
        
    def mossePossibili(self, partita):
        mPossibili = []
        p = self.posizione
        letters = 'abcdefgh'
        numbers = '12345678'
        for a in letters:
            for i in numbers:
                q = a+i
                if self.mossaLecita(partita,p+q):
                    mPossibili.append(p+q)
        return mPossibili
    
    def __eq__(self, pezzo):
        if type(pezzo) != type(self):
            return False
        if self.nome == pezzo.nome and self.colore == pezzo.colore:
            return True
        
class Re(Pezzo):
    def __init__(self, pos, col = BIANCO, storiaPos = False, mosso = False):
        car = '♔' if col == BIANCO else '♚'
        super().__init__(pos, col, np.inf, 'RE', car, reAttacca, mlRe)
        if storiaPos:
            self.storiaPosizioni = storiaPos
        self.mosso = mosso
        
    def copia(self):
        x = Pezzo.copia(self)
        x.mosso = self.mosso
        return x
        
class Regina(Pezzo):
    def __init__(self, pos, col = BIANCO, storiaPos = False):
        car = '♕' if col == BIANCO else '♛'
        super().__init__(pos, col, 9, 'REGINA', car, reginaAttacca, mlRegina)
        if storiaPos:
            self.storiaPosizioni = storiaPos
        
class Torre(Pezzo):
    def __init__(self, pos, col = BIANCO, storiaPos = False, mosso = False):
        car = '♖' if col == BIANCO else '♜'
        super().__init__(pos, col, 5, 'TORRE', car, torreAttacca, mlTorre)
        if storiaPos:
            self.storiaPosizioni = storiaPos
        self.mosso = mosso
        
    def copia(self):
        x = Pezzo.copia(self)
        x.mosso = self.mosso
        return x
        
class Cavallo(Pezzo):
    def __init__(self, pos, col = BIANCO, storiaPos = False):
        car = '♘' if col == BIANCO else '♞'
        super().__init__(pos, col, 3, 'CAVALLO', car, cavalloAttacca, mlCavallo)
        if storiaPos:
            self.storiaPosizioni = storiaPos
        
class Alfiere(Pezzo):
    def __init__(self, pos, col = BIANCO, storiaPos = False):
        car = '♗' if col == BIANCO else '♝'
        super().__init__(pos, col, 3, 'ALFIERE', car, alfiereAttacca, mlAlfiere)
        if storiaPos:
            self.storiaPosizioni = storiaPos
        
class Pedone(Pezzo):
    def __init__(self, pos, col = BIANCO, storiaPos = False, appenaMossoDoppio = False):
        car = '♙' if col == BIANCO else '♟'
        super().__init__(pos, col, 1, 'PEDONE', car, pedoneAttacca, mlPedone)
        if storiaPos:
            self.storiaPosizioni = storiaPos
        self.appenaMossoDoppio = appenaMossoDoppio
        
    def copia(self):
        x = Pezzo.copia(self)
        x.appenaMossoDoppio = self.appenaMossoDoppio
        return x

#Funzioni per shiftare le posizioni
def up(posizione):
    a, i = posizione
    return a+str(int(i)+1) if int(i) < 8 else None
def down(posizione):
    a, i = posizione
    return a+str(int(i)-1) if int(i) > 1 else None
def left(posizione):
    a, i = posizione
    letters = 'abcdefgh'
    if a == 'a':
        return None
    return letters[letters2ind(a)-2]+i
def right(posizione):
    a, i = posizione
    letters = 'abcdefgh'
    if a == 'h':
        return None
    return letters[letters2ind(a)]+i
        
###############################################################################
#                                                                             #
#   Scacchiera: Classe, metodi e funzioni                                     #
#                                                                             #
############################################################################### 
    
class Scacchiera():
    def __init__(self, configurazionePersonalizzata = None):
        global tInitScacchiera
        t = time.time()
        self.letters = 'abcdefgh'
        self.posizioni = []
        d = dict()
        if configurazionePersonalizzata == None:# Nuova Partita
            #Pedoni ♙♟
            for a in self.letters:
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
                if configurazionePersonalizzata[posizione] != None:
                    d[posizione] = configurazionePersonalizzata[posizione].copia()
        self.pezzi = d
        tInitScacchiera += time.time() - t
        
    def getPezzo(self, p = None):
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
            for a in self.letters:
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
            for a in self.letters:
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
        txt += '\n   A B C D E F G H'
        print(txt)
    
    def getPezzi(self):
        pezzi = []
        for pos in self.pezzi:
            pezzi.append(self.pezzi[pos])
        return pezzi
    
    def getBianchi(self):
        bianchi = []
        for pos in self.pezzi:
            if self.pezzi[pos].colore == BIANCO:
                bianchi.append(self.pezzi[pos])
        return bianchi
    
    def getNeri(self):
        neri = []
        for pos in self.pezzi:
            if self.pezzi[pos].colore == NERO:
                neri.append(self.pezzi[pos])
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
    
    def checkScaccoBianco(self):
        '''Ritorna True se il bianco è sottoscacco, False altrimenti'''
        neri = self.getNeri()
        q = self.getReBianco().posizione
        for pezzo in neri:
            if pezzo.attacca(self, q):
                return True
        return False
    
    def checkScaccoNero(self):
        '''Ritorna True se il nero è sottoscacco, False altrimenti'''
        bianchi = self.getBianchi()
        q = self.getReNero().posizione
        for pezzo in bianchi:
            if pezzo.attacca(self, q):
                return True
        return False

#Funzioni per stabilire se un pezzo sta attaccando* una data casella
# Con attaccare si intende possibilità di sostituirsi in una casella ad un 
# pezzo avversario ipotizzato essere in posizione d'arrivo. Per i PEDONI questo
# NON coincide con la possibilità di movimento.
        
def pedoneAttacca(scacchiera, pedone, casella):
    pos = pedone.posizione
    if pedone.colore == BIANCO:
        if not up(pos) == None:
            if right(up(pos)) == casella or left(up(pos)) == casella:
                return True
    if pedone.colore == NERO:
        if not down(pos) == None:
            if right(down(pos)) == casella or left(down(pos)) == casella:
                return True
    return False

def torreAttacca(scacchiera, torre, casella):
    letters = 'abcdefgh'
    p = torre.posizione; q = casella;
    pa, p1 = p; qa, q1 = q;
    if pa == qa and p1 != q1: # Stessa Colonna
        start, end = (p, q) if p1 < q1 else (q, p)
        for i in range(int(start[1]) + 1,int(end[1])):
            if scacchiera.getPezzo(pa+str(i)) != None:
                return False
        return True
    if pa != qa and p1 == q1: # Stessa Riga
        start, end = (p, q) if pa < qa else (q, p)
        for a in range(letters2ind(start[0]), letters2ind(end[0])-1):
            if scacchiera.getPezzo(letters[a]+p1) != None:
                return False
        return True

def cavalloAttacca(scacchiera, cavallo, casella):
    p = cavallo.posizione; q = casella; pa, p1, qa, q1 = p+q;
    if pa == qa or p1 == q1:
        return False
    elif dist(p,q) == 3:
        return True
    return False

def alfiereAttacca(scacchiera, alfiere, casella):
    pos = alfiere.posizione
    k = letters2ind(pos[0]) - int(pos[1])
    if letters2ind(casella[0]) - int(casella[1]) == k:
        #Diagonale Ascendente:
        ok = True
        start, end = (pos, casella) if pos[1] < casella[1] else (casella, pos)
        #Start è quello più in basso
        while start != end:
            start = up(right(start))
            if start != end and scacchiera.getPezzo(start) != None:
                ok = False; break;    
        if ok:
            return True
    k = letters2ind(pos[0]) + int(pos[1])
    if letters2ind(casella[0]) + int(casella[1]) == k:
        #Diagonale Discendente
        ok = True
        start, end = (pos, casella) if pos[1] < casella[1] else (casella, pos)
        #Start è quello più in basso
        while start != end:
            start = up(left(start))
            if start != end and scacchiera.getPezzo(start) != None:
                ok = False; break;    
        if ok:
            return True
    return False

def reginaAttacca(scacchiera, regina, casella):
    return torreAttacca(scacchiera, regina, casella) or alfiereAttacca(scacchiera, regina, casella)

def reAttacca(scacchiera, re, casella):
    pos = re.posizione
    pa, p1 = pos; qa, q1 = casella
    c1 = dist(pos, casella) == 1
    c2 = dist(pos, casella) == 2
    c3 = pa != qa and p1 != q1
    return c1 or (c2 and c3)

###############################################################################
#                                                                             #
#   Partita: Classe, metodi e funzioni                                        #
#                                                                             #
###############################################################################         

class Partita():
    def __init__(self, scacchiera = None, configurazionePersonalizzata = None, mode = '2p', stampa = True, biancoAI = lambda p: randomAI(p), neroAI = lambda p: randomAI(p)):
        self.mode = mode
        self.scacchiera = Scacchiera(configurazionePersonalizzata) if scacchiera == None else scacchiera
        self.turno = BIANCO
        self.mosse = []
        self.mosseSenzaMangiare = 0
        self.tempiBianco = []
        self.tempiNero = []
        self.storiaConfigurazioni = [self.scacchiera]
        self.ultimaMossaIrreversibile = 0
        self.biancoArroccato = False
        self.neroArroccato = False
        self.mangiatiBianchi = []
        self.mangiatiNeri = []
        self.stampa = stampa
        self.biancoAI = biancoAI
        self.neroAI = neroAI
        self.esito = 'NESSUNO'
        
    def stampaStoria(self):
        for s in self.storiaConfigurazioni:
            s.stampa()
            
    def irreversibile(self, mossa):
        mossaPedone = self.scacchiera.getPezzo(mossa[:2]).nome == 'PEDONE'
        arrocco = self.scacchiera.getPezzo(mossa[:2]).nome == 'RE'
        arrocco = arrocco and dist(mossa[:2], mossa[2:]) == 2
        mangiato = self.scacchiera.getPezzo(mossa[2:]) != None
        return mossaPedone or arrocco or mangiato
    
    def checkLegale(self, mossa):
        if len(mossa) != 4:
            return False
        letters = 'abcdefgh'
        numbers = '12345678'
        pa, p1, qa, q1 = mossa; p, q = (pa+p1, qa+q1)
        if not (pa in letters and qa in letters and p1 in numbers and q1 in numbers):
            return False
        mangiato = self.scacchiera.getPezzo(q) != None
        pezzo = self.scacchiera.getPezzo(p)
        if pezzo == None:
            return False
        if pezzo.colore != self.turno:
            return False
        res = pezzo.mossaLecita(self, mossa, False)
        if res:
            enpassant = pezzo.nome == 'PEDONE' and pa != qa and self.scacchiera.getPezzo(q) == None
            if mangiato or enpassant:
                self.mosseSenzaMangiare = 0
        return res
    
    def muovi(self, mossa):
        # Sintassi
        if len(mossa) != 4:
            return False
        letters = 'abcdefgh'
        numbers = '12345678'
        pa, p1, qa, q1 = mossa; p, q = (pa+p1, qa+q1)
        if not (pa in letters and qa in letters and p1 in numbers and q1 in numbers):
            return False
        pezzo = self.scacchiera.getPezzo(p)
        mangiato = self.scacchiera.getPezzo(q)
        # Selezionato un pezzo giusto
        if pezzo == None:
            return False
        if pezzo.colore != self.turno:
            return False
        # Mangiando sé stesso
        if mangiato != None and mangiato.colore == self.turno:
            return False
        return pezzo.mossaLecita(self, mossa, True)
    
    def gioca(self, listaMosse = []):
        mossa = 'inizio'
        listaMosse.reverse()
        t = time.time()
        fine = False
        while mossa[:2] != mossa[2:] and not fine:
            if self.stampa: self.scacchiera.stampa()
            fine = self.checkFine()
            if not fine:
                # Acquisisci Mossa
                colore = 'BIANCO' if self.turno == BIANCO else 'NERO'
                if self.mode == '2p':
                    mossa = input('Tocca al '+colore+': ')
                elif self.mode == '1p':
                    mossa = self.neroAI(self) if self.turno == NERO else input('Tocca al '+colore+': ')
                elif self.mode == '0p':
                    mossa = self.biancoAI(self) if self.turno == BIANCO else self.neroAI(self)
                elif self.mode == 'listaMosse':
                    mossa = listaMosse.pop() if len(listaMosse) > 0 else 'a1a1'
                irreversibile = self.irreversibile(mossa)
                #ok = self.checkLegale(mossa)
                ok = self.muovi(mossa)
                if ok:
                    if irreversibile:
                        self.ultimaMossaIrreversibile = len(self.storiaConfigurazioni)
                    deltaT = time.time() - t
                    t = time.time()
                    self.turno = BIANCO if self.turno == NERO else NERO
                    self.mosse.append(mossa)
                    self.mosseSenzaMangiare += 1
                    self.storiaConfigurazioni.append(self.scacchiera)
                    if self.turno == BIANCO:
                        self.tempiNero.append(deltaT)
                    else:
                        self.tempiBianco.append(deltaT)
                    pezzi = self.scacchiera.getNeri() if self.turno == NERO else self.scacchiera.getBianchi()
                    for pezzo in pezzi:
                        if pezzo.nome == 'PEDONE':
                            pezzo.appenaMossoDoppio = False
                else:
                    if self.stampa: print('Mossa Illegale.')
        if self.stampa: self.stampaRisultato()
                
    def getTempoTot(self, colore):
        if colore == BIANCO:
            return sum(self.tempiBianco)
        else:
            return sum(self.tempiNero)
        
    def esploraStorico(self):
        for s in self.storiaConfigurazioni:
            input('Clicca invio per Proseguire')
            s.stampa()
            
    def mossePossibili(self):
        pezzi = self.scacchiera.getBianchi() if self.turno == BIANCO else self.scacchiera.getNeri()
        mosse = []
        for pezzo in pezzi:
            mosse += pezzo.mossePossibili(self)
        return mosse        
            
    def checkStallo(self):
        sottoScacco = self.scacchiera.checkScaccoBianco() if self.turno == BIANCO else self.scacchiera.checkScaccoNero()
        if not sottoScacco:
            mosse = self.mossePossibili()
            if len(mosse) == 0:
                self.esito = 'STALLO.'
                return True
        return False
    
    def checkPatta50Mosse(self):
        if self.mosseSenzaMangiare >= 50 :
            self.esito = 'PATTA per 50 mosse senza mangiare.'
            return True
        return False
    
    def checkRipetizione(self):
        count = 1
        for i in range(self.ultimaMossaIrreversibile, len(self.storiaConfigurazioni)-1):
            config = self.storiaConfigurazioni[i]
            if configurazioniUguali(config, self.storiaConfigurazioni[-1]):
                turno = NERO if i%2 else BIANCO
                stessoTurno = self.turno == turno
                if stessoTurno:
                    count += 1
        if count >= 3:
            self.esito = 'PATTA per ripetizione.'
            return True
        return False
        
    def checkPatta(self):
        return self.checkStallo() or self.checkPatta50Mosse() or self.checkRipetizione()
    
    def checkVinceBianco(self):
        if self.turno == NERO and self.scacchiera.checkScaccoNero():
            mosse = self.mossePossibili()
            if len(mosse) == 0:
                self.esito = 'Vince il BIANCO.'
                return True
        return False
    
    def checkVinceNero(self):
        if self.turno == BIANCO and self.scacchiera.checkScaccoBianco():
            mosse = self.mossePossibili()
            if len(mosse) == 0:
                self.esito = 'Vince il NERO.'
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
        
    def salva(self, nome = 'partita.txt'):
        file = open(nome, "w")
        file.write(nome)
        for configurazione in self.storiaConfigurazioni:
            file.write(str(configurazione)+'\n')
        file.write('\nSequenza Mosse:\n\n')
        for i in range(len(self.mosse)):
            mossa = self.mosse[i]
            autore, tempi = ('BIANCO', self.tempiBianco) if not i % 2 else ('NERO', self.tempiNero)
            file.write('\t'+str(i)+'.\t'+mossa+' giocata dal '+autore+'\tin '+str(int(tempi[i//2]*1000)/1000)+' s\n')
        file.write('\nTotale Tempo impiegato dal BIANCO: ' + str(int(sum(self.tempiBianco)*1000)/1000) + ' s\n')
        file.write('Totale Tempo impiegato dal NERO:   ' + str(int(sum(self.tempiNero)*1000)/1000) + ' s\n')
        file.write('\nesito: '+self.esito+'.')
        file.close()
            
# Funzioni ammissibilità mosse
        
# Funzioni Generali
        
def mlGenerale(partita, mossa):
    '''Controlla se si vuole muovere un pezzo sopra ad un proprio pezzo'''
    c1 = partita.scacchiera.getPezzo(mossa[:2]).colore
    if partita.scacchiera.getPezzo(mossa[2:]) != None:
        c2 = partita.scacchiera.getPezzo(mossa[2:]).colore
        if c1 == c2:
            return False
    return True

def mlSottoScacco(ok, futuro, partita, muovi):
    if ok:
        condizione = not futuro.checkScaccoBianco() if partita.turno == BIANCO else not futuro.checkScaccoNero()
        if condizione:
            if muovi:
                partita.scacchiera = futuro
            return True
    return False

def noSpeciali(partita, mossa, muovi, chiAttacca):
    if mlGenerale(partita, mossa):
        futuro = Scacchiera(partita.scacchiera.pezzi)
        ok = False
        pa, p1, qa, q1 = mossa; p, q = pa+p1, qa+q1;
        pezzo = futuro.getPezzo(p)
        if chiAttacca(futuro, pezzo, q): # <----
            mangiato = futuro.getPezzo(q)
            if mangiato == None:
                sposta(futuro, mossa, muovi = muovi) # <-----
                ok = True
            else:
                if pezzo.colore != mangiato.colore:
                    sposta(futuro, mossa, partita, muovi = muovi)
                    ok = True
        return mlSottoScacco(ok, futuro, partita, muovi)
    return False
    
# Funzioni Specifiche   
    
def mlCavallo(partita, mossa, muovi = False):
    return noSpeciali(partita, mossa, muovi, cavalloAttacca)

def mlAlfiere(partita, mossa, muovi = False):
    return noSpeciali(partita, mossa, muovi, alfiereAttacca)

def mlTorre(partita, mossa, muovi = False):
    return noSpeciali(partita, mossa, muovi, torreAttacca)

def mlRegina(partita, mossa, muovi = False):
    return noSpeciali(partita, mossa, muovi, reginaAttacca)

def mlPedone(partita, mossa, muovi = False):
    if mlGenerale(partita, mossa):
        futuro = Scacchiera(partita.scacchiera.pezzi)
        ok = False
        pa, p1, qa, q1 = mossa; p, q = pa+p1, qa+q1;
        pezzo = futuro.getPezzo(p)
        if pezzo == None: return False
        if pezzo.colore == BIANCO:
            #Mangiare
            if not ok and up(p) != None:
                if (right(p) != None and q == right(up(p))) or (left(p) != None and q == left(up(p))):
                    if not ok and futuro.getPezzo(q) != None:
                        mangiato = futuro.getPezzo(q)
                        if mangiato.colore == NERO: 
                            sposta(futuro,mossa, partita, muovi = muovi)
                            if q[1] == '8': #Promozione
                                futuro.pezzi[q] = Regina(q, BIANCO, pezzo.storiaPosizioni)
                            ok = True
                    if not ok and futuro.getPezzo(down(q)) != None:
                        mangiato = futuro.getPezzo(down(q))
                        if mangiato.colore == NERO and mangiato.nome == 'PEDONE' and mangiato.appenaMossoDoppio == True:
                            sposta(futuro, mossa, muovi = muovi)
                            partita.mangiatiNeri.append(mangiato)
                            futuro.pezzi.pop(down(q))
                            ok = True # Enpassant
            #Avanzare
            if not ok and up(p) == q:
                if futuro.getPezzo(q) == None:
                    sposta(futuro, mossa, muovi = muovi)
                    if q[1] == '8': #Promozione
                        futuro.pezzi[q] = Regina(q, BIANCO, pezzo.storiaPosizioni)
                    ok = True
            if not ok and up(p) != None and up(up(p)) == q and p[1] == '2':
                if futuro.getPezzo(up(p)) == None == futuro.getPezzo(q):
                    pezzo.appenaMossoDoppio = True
                    sposta(futuro, mossa, muovi = muovi)
                    ok = True  
        if pezzo.colore == NERO:
            #Mangiare
            if not ok and down(p) != None:
                if (down(p) != None and q == right(down(p))) or (left(p) != None and q == left(down(p))):
                    if not ok and futuro.getPezzo(q) != None:
                        mangiato = futuro.getPezzo(q)
                        if mangiato.colore == BIANCO: 
                            sposta(futuro, mossa, partita, muovi = muovi)
                            if q[1] == '1': #Promozione
                                futuro.pezzi[q] = Regina(q, NERO, pezzo.storiaPosizioni)
                            ok = True #Normale
                    if not ok and futuro.getPezzo(up(q)) != None:
                        mangiato = futuro.getPezzo(up(q))
                        if mangiato.colore == BIANCO and mangiato.nome == 'PEDONE' and mangiato.appenaMossoDoppio == True:
                            sposta(futuro, mossa, muovi = muovi)
                            partita.mangiatiNeri.append(mangiato)
                            futuro.pezzi.pop(up(q))
                            ok = True # Enpassant
            #Avanzare
            if not ok and down(p) == q:
                if futuro.getPezzo(q) == None:
                    sposta(futuro, mossa, muovi = muovi)
                    if q[1] == '1': #Promozione
                        futuro.pezzi[q] = Regina(q, NERO, pezzo.storiaPosizioni)
                    ok = True
            if not ok and down(p) != None and down(down(p)) == q and p[1] == '7':
                if futuro.getPezzo(down(p)) == None == futuro.getPezzo(q):
                    pezzo.appenaMossoDoppio = True
                    sposta(futuro, mossa, muovi = muovi)
                    ok = True
        return mlSottoScacco(ok, futuro, partita, muovi)
    return False

def mlRe(partita, mossa, muovi = False):
    if mlGenerale(partita, mossa):
        futuro = Scacchiera(partita.scacchiera.pezzi)
        pa, p1, qa, q1 = mossa; p = pa+p1;
        re = futuro.getPezzo(p)
        ok = noSpeciali(partita, mossa, muovi, reAttacca)
        if ok:
            return True
        # Gestiamo l'arrocco
        if re.colore == BIANCO:
            if not ok and mossa == 'e1c1': # Arrocco Lungo
                torre = futuro.getPezzo('a1')
                c1 = torre != None and torre.colore == BIANCO and torre.nome == 'TORRE'
                if c1:
                    c2 = not torre.mosso and not re.mosso
                    if c2:
                        c3 = futuro.getPezzo('b1') == None
                        c3 = futuro.getPezzo('c1') == None and c3
                        c3 = futuro.getPezzo('d1') == None and c3
                        if c3:
                            c4 = not futuro.checkScaccoBianco()
                            if c4:
                                c5 = True
                                neri = futuro.getNeri()
                                for pezzo in neri:
                                    if pezzo.attacca(futuro, 'd1'):
                                        c5 = False; break;
                                if c5:
                                    sposta(futuro, mossa, muovi = muovi)
                                    sposta(futuro, 'a1d1', muovi = muovi)
                                    ok = True
            if not ok and mossa == 'e1g1': # Arrocco Corto
                torre = futuro.getPezzo('h1')
                c1 = torre != None and torre.colore == BIANCO and torre.nome == 'TORRE'
                if c1:
                    c2 = not torre.mosso and not re.mosso
                    if c2:
                        c3 = futuro.getPezzo('f1') == None
                        c3 = futuro.getPezzo('g1') == None and c3
                        if c3:
                            c4 = not futuro.checkScaccoBianco()
                            if c4:
                                c5 = True
                                neri = futuro.getNeri()
                                for pezzo in neri:
                                    if pezzo.attacca(futuro, 'f1'):
                                        c5 = False; break;
                                if c5:
                                    sposta(futuro, mossa, muovi = muovi)
                                    sposta(futuro, 'h1f1', muovi = muovi)
                                    ok = True
        if re.colore == NERO:
            if not ok and mossa == 'e8c8': # Arrocco Lungo
                torre = futuro.getPezzo('a8')
                c1 = torre != None and torre.colore == NERO and torre.nome == 'TORRE'
                if c1:
                    c2 = not torre.mosso and not re.mosso
                    if c2:
                        c3 = futuro.getPezzo('b8') == None
                        c3 = futuro.getPezzo('c8') == None and c3
                        c3 = futuro.getPezzo('d8') == None and c3
                        if c3:
                            c4 = not futuro.checkScaccoNero()
                            if c4:
                                c5 = True
                                bianchi = futuro.getBianchi()
                                for pezzo in bianchi:
                                    if pezzo.attacca(futuro, 'd8'):
                                        c5 = False; break;
                                if c5:
                                    sposta(futuro, mossa, muovi = muovi)
                                    sposta(futuro, 'a8d8', muovi = muovi)
                                    ok = True
            if not ok and mossa == 'e8g8': # Arrocco Corto
                torre = futuro.getPezzo('h8')
                c1 = torre != None and torre.colore == NERO and torre.nome == 'TORRE'
                if c1:
                    c2 = not torre.mosso and not re.mosso
                    if c2:
                        c3 = futuro.getPezzo('f8') == None
                        c3 = futuro.getPezzo('g8') == None and c3
                        if c3:
                            c4 = not futuro.checkScaccoNero()
                            if c4:
                                c5 = True
                                bianchi = futuro.getBianchi()
                                for pezzo in bianchi:
                                    if pezzo.attacca(futuro, 'f8'):
                                        c5 = False; break;
                                if c5:
                                    sposta(futuro, mossa, muovi = muovi)
                                    sposta(futuro, 'h8f8', muovi = muovi)
                                    ok = True
        return mlSottoScacco(ok, futuro, partita, muovi)
    return False
    
# Altre funzioni

def sposta(scacchiera, mossa, partita = None, muovi = False):
    pa, p1, qa, q1 = mossa; p = pa+p1; q = qa+q1;
    if scacchiera.getPezzo(p) != None :
        if (scacchiera.getPezzo(p).nome == 'RE' or scacchiera.getPezzo(p).nome == 'TORRE') and not scacchiera.getPezzo(p).mosso:
            scacchiera.getPezzo(p).mosso = True
        mangiato = scacchiera.getPezzo(q)
        scacchiera.pezzi[q] = scacchiera.getPezzo(p)
        scacchiera.pezzi[q].setPosizione(q)
        if muovi:
            if partita != None:
                if mangiato != None:
                    if mangiato.colore == BIANCO: partita.mangiatiBianchi.append(mangiato)
                    if mangiato.colore == NERO: partita.mangiatiNeri.append(mangiato)
            scacchiera.getPezzo(q).storiaPosizioni.append(q)
        scacchiera.pezzi.pop(p)
        
def configurazioniUguali(c1, c2):
    letters = 'abcdefgh'
    numbers = '12345678'
    for a in letters:
        for i in numbers:
            p = a+i
            pezzo1 = c1.getPezzo(p); pezzo2 = c2.getPezzo(p);
            if not pezzo1 == pezzo2:
                return False
            elif not pezzo1 == None:
                if pezzo1.nome == 'RE' or pezzo1.nome == 'TORRE':
                    if not pezzo1.mosso == pezzo2.mosso:
                        return False
                # Controlla possibiltà di enpassant
    return True
    
def randomAI(partita):
    mosse = partita.mossePossibili()
    n = len(mosse)
    if n == 0:
        return 'a1a1'
    i = rn.randint(0,n-1)
    return mosse[i]
    
###############################################################################
#                                                                             #
#   Sezione dedicata a calcolo e visualizzazione delle distanze dei pezzi     #
#                                                                             #
###############################################################################
    
def distanza(pezzo, casella):
    if pezzo.posizione == casella:
        return 0
    s = Scacchiera({pezzo.posizione:pezzo})
    letters = 'abcdefgh'
    numbers = '12345678'   
    Tipo = type(pezzo)
    mosse = set([pezzo.posizione+pezzo.posizione])
    controllati = set()
    ok = False; c = True; d = 0
    while not ok and c:
        mosse2 = set()
        c = False
        for mossa in mosse:
            p = mossa[2:]
            if not p in controllati:
                pezzo = Tipo(p)
                s = Scacchiera({p:pezzo})
                for a in letters:
                    for i in numbers:
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
    letters = 'abcdefgh'
    numbers = '12345678'
    for i in range(8):
        for j in range(8):
            p = letters[j]+numbers[i]
            M[7-i,j] = distanza(pezzo, p)
    colorMap = mpl.cm.cool
    fig, ax = plt.subplots()
    im = ax.imshow(M, cmap=colorMap)
    ax.set_title('Distanze per mosse necessarie\n'+pezzo.nome+' in '+pezzo.posizione)
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

#s = Scacchiera()
#print(s)
#t = Scacchiera(s.pezzi)

#game = Partita(mode = '0p')
#game.gioca()

#Finali = []
#for i in tqdm(range(50)):
#    game = Partita(mode = '0p', stampa = False)
#    game.gioca()
#    Finali.append([game.storiaConfigurazioni[-1], game.esito])
#file_uno = open("studioFinaliCercandoErrori2.txt", "w")
#for finale in Finali:
#    file_uno.write(str(finale[0])+'\t\t\t\t\t\t\t\t\t\t'+str(finale[1])+'\n\n')
#file_uno.close()
    
#game = Partita(mode = 'listaMosse')
#game.gioca(['e2e4',
# 'e7e5',
# 'e1e2',
# 'e8e7',
# 'e2e1',
# 'e7e8',
# 'e1e2',
# 'e8e7',
# 'e2e1',
# 'e7e8'])
    
#game = Partita(mode = '0p')
#game.gioca()
    
#c = Cavallo('b1')
#d = distanza(c, 'b1')
#print(d)

#a = Alfiere('c1')
#dd = distanza(a, 'e2')
#print(dd)
    
#c = Cavallo('a1')
#t = Torre('a1')
#a = Alfiere('a1')
#r = Re('a1')
#reg = Regina('a1')
#pezzi = [c,t,a,r,reg] 
#for pezzo in pezzi:
#    visualizzaMetrica(pezzo)
    
#game = Partita(mode = '0p')
#game.gioca()
#game.salva('partitaRandom3.txt')

for i in tqdm(range(25)):
    game = Partita(mode = '0p', stampa = False)
    game.gioca()
    
###############################################################################
#                                                                             #
#   Commenti per idee e memo                                                  #
#                                                                             #
############################################################################### 
    
# Scrivi i setCampo e i getCampo
#
# La lentezza è dovuta alla continua creazione di 'futuro'
# 
# Gestire il checkSottoScacco NON creando scacchiere fittizie e poi in caso
# positivo non salvarle, bensì muovendo sulla scacchiera corrente e, in caso 
# positivo tornare indietro inserendo l'opzione mossaInversa.
#
# Pareggi:
#   Differenziare tra pareggio proposto e obbligato
#   Pareggio per ripetizione:
#       controlla possibilità di enpassant

tTot = time.time() - tTot
print('\n...Esecuzione in '+str(int(tTot*1000)/1000) + ' secondi.')