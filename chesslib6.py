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

modalita = ['0p', '1p', '2p', 'listaMosse']
tipiMosse = ['Sposta', 'Mangia', 'Avanza1', 'Avanza2', 'Pedone Mangia',
             'Enpassant', 'Arrocco Corto', 'Arrocco Lungo', 
             'Promozione Mangia', 'Promozione Avanza']
backGround = '\u001b[46m' 
reset = '\u001b[0m'    
l2i = {'a':1,'b':2,'c':3,'d':4,'e':5,'f':6,'g':7,'h':8}

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
tCopia = 0              # Tempo speso acopiare i pezzi
tInitScacchiera = 0     # Non disgiunto dal precedente
tIndietro = 0
indietro = 0

BIANCO = 0
NERO = 1

###############################################################################
#                                                                             #
#   Funzioni generiche utili                                                  #  
#                                                                             #
###############################################################################

def letters2ind(a):
    return l2i[a]

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
        caselle = self.getCaselleRaggiungibili()
        for q in caselle:
            mossa = p+q
            ok, tipo = partita.checkLegale(mossa)
            if ok:
                mPossibili.append(mossa)
        return mPossibili
    
    def getCaselleRaggiungibili(self):
        caselle = []
        letters = 'abcdefgh'
        numbers = '12345678'
        for a in letters:
            for i in numbers:
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
    def __init__(self, pos, col = BIANCO, storiaPos = False):
        car = '♔' if col == BIANCO else '♚'
        super().__init__(pos, col, np.inf, 'RE', car, reAttacca, mlRe)
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
            caselleArrocco = ['c1', 'g1'] if self.colore == BIANCO else ['c8','g8']
            caselle += caselleArrocco
        return caselle
        
class Regina(Pezzo):
    def __init__(self, pos, col = BIANCO, storiaPos = False):
        car = '♕' if col == BIANCO else '♛'
        super().__init__(pos, col, 9, 'REGINA', car, reginaAttacca, mlRegina)
        if storiaPos:
            self.storiaPosizioni = storiaPos
        
class Torre(Pezzo):
    def __init__(self, pos, col = BIANCO, storiaPos = False):
        car = '♖' if col == BIANCO else '♜'
        super().__init__(pos, col, 5, 'TORRE', car, torreAttacca, mlTorre)
        if storiaPos:
            self.storiaPosizioni = storiaPos
    
    def getCaselleRaggiungibili(self):
        pa, p1 = self.posizione
        caselle = []
        letters = 'abcdefgh'
        numbers = '12345678'
        for a in letters:
            caselle.append(a+p1)
        for i in numbers:
            caselle.append(pa+i)
        return caselle
        
class Cavallo(Pezzo):
    def __init__(self, pos, col = BIANCO, storiaPos = False):
        car = '♘' if col == BIANCO else '♞'
        super().__init__(pos, col, 3, 'CAVALLO', car, cavalloAttacca, mlCavallo)
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
        car = '♗' if col == BIANCO else '♝'
        super().__init__(pos, col, 3, 'ALFIERE', car, alfiereAttacca, mlAlfiere)
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
        txt += '\n   A B C D E F G H \n'
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
    letters = 'abcdefgh'
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
            if scacchiera.getPezzo(letters[a]+p1) != None:
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
    #########
#    p = alfiere.posizione; q = casella;
#    k = letters2ind(p[0]) - int(p[1])
#    if letters2ind(q[0]) - int(q[1]) == k:
#        #Diagonale Ascendente:
#        ok = True
#        start, end = (p, q) if p[1] < q[1] else (q, p)
#        #Start è quello più in basso
#        while start != end:
#            start = up(right(start))
#            if start != end and scacchiera.getPezzo(start) != None:
#                ok = False; break;    
#        if ok:
#            return True
#    k = letters2ind(p[0]) + int(p[1])
#    if letters2ind(q[0]) + int(q[1]) == k:
#        #Diagonale Discendente
#        ok = True
#        start, end = (p, q) if p[1] < q[1] else (q, p)
#        #Start è quello più in basso
#        while start != end:
#            start = up(left(start))
#            if start != end and scacchiera.getPezzo(start) != None:
#                ok = False; break;    
#        if ok:
#            return True
#    return False

def reginaAttacca(scacchiera, regina, casella):
    return torreAttacca(scacchiera, regina, casella) or alfiereAttacca(scacchiera, regina, casella)

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
    def __init__(self, scacchiera = None, configurazionePersonalizzata = None, mode = '2p', stampa = True, biancoAI = lambda p: randomAI(p), neroAI = lambda p: randomAI(p)):
        self.mode = mode
        self.scacchiera = Scacchiera(configurazionePersonalizzata) if scacchiera == None else scacchiera
        self.turno = BIANCO
        self.mosse = []
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
        
    def stampaStoria(self):
        for s in self.storiaConfigurazioni:
            s.stampa()
            
    def cambiaTurno(self):
        self.turno = NERO if self.turno == BIANCO else BIANCO
            
    def irreversibile(self, mossa, tipoMossa):
        mossaPedone = True if tipoMossa in ('Avanza1', 'Avanza2', 'Pedone Mangia', 'Enpassant', 'Promozione Avanza', 'Promozione Mangia') else False
        arrocco = True if tipoMossa[:7] == 'Arrocco' else False
        mangiato = True if tipoMossa in ('Mangia', 'Enpassant', 'Promozione Mangia') else False
        return mossaPedone or arrocco or mangiato
    
    def checkLegale(self, mossa):
        # Sintassi
        if len(mossa) != 4:
            return False, None
        letters = 'abcdefgh'
        numbers = '12345678'
        pa, p1, qa, q1 = mossa; p, q = (pa+p1, qa+q1)
        if not (pa in letters and qa in letters and p1 in numbers and q1 in numbers):
            return False, None
        pezzo = self.scacchiera.getPezzo(p)
        mangiato = self.scacchiera.getPezzo(q)
        # Selezionato un pezzo giusto
        if pezzo == None:
            return False, None
        if pezzo.colore != self.turno:
            return False, None
        # Mangiando sé stesso
        if mangiato != None and mangiato.colore == self.turno:
            return False, None
        return pezzo.mossaLecita(self, mossa)
    
    def muovi(self, mossa):
        ok, tipoMossa = self.checkLegale(mossa)
        if ok:
            eseguiMossa(self, mossa, tipoMossa)
            self.cambiaTurno()
            self.mosse.append(mossa)
            self.tipiMosse.append(tipoMossa)
            if tipoMossa in ('Mangia','Enpassant', 'Pedone Mangia', 'Promozione Mangia'):
                self.mosseSenzaMangiare = 0
            else:
                self.mosseSenzaMangiare += 1
            if self.irreversibile(mossa, tipoMossa):
                self.ultimaMossaIrreversibile = len(self.storiaConfigurazioni)
            self.storiaConfigurazioni.append(Scacchiera(self.scacchiera.pezzi))
        return ok
    
    def indietro(self):
        global tIndietro, indietro
        indietro += 1
        t = time.time()
        if len(self.mosse) == 0:
            return
        turno = self.turno
        mossa = self.mosse.pop()
        p, q = (mossa[:2], mossa[2:])
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
            self.scacchiera.pezzi[p] = self.storiaConfigurazioni[-1].getPezzo(p)
        elif tipoMossa == 'Promozione Mangia':
            self.scacchiera.pezzi[p] = self.storiaConfigurazioni[-1].getPezzo(p)
            mangiato = mangiati.pop()
            self.scacchiera.pezzi[mangiato.posizione] = mangiato
        elif tipoMossa == 'Arrocco Corto':
            torre = self.scacchiera.getPezzo('f1') if turno == NERO else self.scacchiera.getPezzo('f8')
            mossaTorre = 'f1h1' if turno == NERO else 'f8h8'
            sposta(self.scacchiera, mossaTorre)
            torre.storiaPosizioni.pop()
            torre.posizione = torre.storiaPosizioni[0]
            self.mosseSenzaMangiare -= 1
        elif tipoMossa == 'Arrocco Lungo':
            torre = self.scacchiera.getPezzo('d1') if turno == NERO else self.scacchiera.getPezzo('d8')
            mossaTorre = 'd1a1' if turno == NERO else 'd8a8'
            sposta(self.scacchiera, mossaTorre)
            torre.storiaPosizioni.pop()
            torre.posizione = torre.storiaPosizioni[0]
            self.mosseSenzaMangiare -= 1
        self.storiaConfigurazioni.pop()
        self.cambiaTurno()
        dt = time.time() - t
        tIndietro += dt
    
    def acquisisciMossa(self, listaMosse):
        colore = 'BIANCO' if self.turno == BIANCO else 'NERO'
        if self.mode == '2p':
            mossa = input('...Tocca al '+colore+': ')
        elif self.mode == '1p':
            mossa = self.neroAI(self) if self.turno == NERO else input('...Tocca al '+colore+': ')
        elif self.mode == '0p':
            mossa = self.biancoAI(self) if self.turno == BIANCO else self.neroAI(self)
        elif self.mode == 'listaMosse':
            mossa = listaMosse.pop() if len(listaMosse) > 0 else 'a1a1'
        return mossa
    
    def gioca(self, listaMosse = []):
        mossa = 'inizio'
        listaMosse.reverse()
        t = time.time()
        fine = False
        while mossa[:2] != mossa[2:] and not fine:
            if self.stampa: self.scacchiera.stampa()
            fine = self.checkFine()
            if not fine:
                if self.stampa:
                    if self.sonoSottoScacco():
                        print('\n\aSCACCO AL RE!')
                mossa = self.acquisisciMossa(listaMosse)
                if mossa == 'back':
                    self.indietro()
                    if self.mode == '1p':
                        self.indietro()
                else:
                    ok = self.muovi(mossa)
                    if ok:
                        deltaT = time.time() - t
                        t = time.time()
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
            stop = input('Clicca invio per Proseguire, stop per concludere:  ')
            if stop == 'stop': break
            s.stampa()
            
    def getPezzi(self):
        return self.scacchiera.getBianchi() if self.turno == BIANCO else self.scacchiera.getNerii()
            
    def sonoSottoScacco(self):
        return self.scacchiera.checkScaccoBianco() if self.turno == BIANCO else self.scacchiera.checkScaccoNero()
            
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
        
    def carica(nome):
        file = open(nome, "r")
        stringhe = file.readlines()
        for i in range(len(stringhe)):
            if stringhe[i] == 'Sequenza Mosse:\n':
                break
        mode = stringhe[6:-2]
        stringhe = stringhe[i+2:]
        mosse = []; tipiMosse = [];
        tempiBianco = []; tempiNero = [];
        letters = 'abcdefgh'
        numbers = '12345678'
        cifre = '0123456789'
        for s in stringhe:
            mossa = ''; tempo = ''; tipo = '';
            lettera = True; numero = False; cercaTempo = True
            for ch in s:
                # Cerca Mossa
                if len(mossa) < 4:
                    if lettera and ch in letters:
                        mossa += ch
                        lettera = False; numero = True
                    elif numero and ch in numbers:
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
        game = Partita(stampa = False, mode='listaMosse')
        game.gioca(mosse)
        game.tempiBianco = tempiBianco
        game.tempiNero = tempiNero
        game.tipiMosse = tipiMosse
        game.mode = mode
        return game
        
    def salva(self, nome = 'partita.txt'):
        file = open(nome, "w")
        file.write(nome)
        file.write('\nmode: '+self.mode+'\n')
        for configurazione in self.storiaConfigurazioni:
            file.write(str(configurazione)+'\n')
        file.write('\nSequenza Mosse:\n\n')
        for i in range(len(self.mosse)):
            mossa = self.mosse[i]
            tipoMossa = self.tipiMosse[i]
            autore, tempi = ('BIANCO', self.tempiBianco) if not i % 2 else ('NERO', self.tempiNero)
            file.write('\t'+str(i)+'.\t'+mossa+' giocata dal '+autore+'\tin '+str(int(tempi[i//2]*100000)/100000)+' s. ('+tipoMossa+')\n')
        file.write('\nTotale Tempo impiegato dal BIANCO: ' + str(int(sum(self.tempiBianco)*100000)/100000) + ' s\n')
        file.write('Totale Tempo impiegato dal NERO:   ' + str(int(sum(self.tempiNero)*100000)/100000) + ' s\n')
        file.write('\nesito: '+self.esito+'.')
        file.close()
            
# Funzioni ammissibilità mosse
        
# Funzioni Generali

def noSpeciali(partita, mossa, chiAttacca):
    pa, p1, qa, q1 = mossa; p, q = pa+p1, qa+q1;
    pezzo = partita.scacchiera.getPezzo(p)
    mangiato = partita.scacchiera.getPezzo(q)
    if chiAttacca(partita.scacchiera, pezzo, q): 
        sposta(partita.scacchiera, mossa)
        partita.scacchiera.pezzi[q].posizione = q
        sottoScacco = partita.sonoSottoScacco()
        partita.scacchiera.pezzi[q].posizione = p
        sposta(partita.scacchiera, q+p)
        tipo = 'Sposta'
        if mangiato != None:
            tipo = 'Mangia'
            partita.scacchiera.pezzi[q] = mangiato
        if not sottoScacco:
            return True, tipo
    return False, None
    
# Funzioni Specifiche   
    
def mlCavallo(partita, mossa):
    return noSpeciali(partita, mossa, cavalloAttacca)

def mlAlfiere(partita, mossa):
    return noSpeciali(partita, mossa, alfiereAttacca)

def mlTorre(partita, mossa):
    return noSpeciali(partita, mossa, torreAttacca)

def mlRegina(partita, mossa):
    return noSpeciali(partita, mossa, reginaAttacca)

def mlPedone(partita, mossa):
    pa, p1, qa, q1 = mossa; p, q = pa+p1, qa+q1;
    if dist(p, q) > 2:
        return False, None
    pezzo = partita.scacchiera.getPezzo(p) # So che è un pedone
    mangiato = partita.scacchiera.getPezzo(q)
    avanza = up if pezzo.colore == BIANCO else down
    if avanza(p) != None:
        # Provo ad Avanzare
        if avanza(p) == q or (avanza(avanza(p)) == q and pezzo.mosso() == False and partita.scacchiera.getPezzo(avanza(p)) == None): 
            if mangiato == None:
                sposta(partita.scacchiera, mossa)
                sottoScacco = partita.sonoSottoScacco()
                sposta(partita.scacchiera, q+p)
                if not sottoScacco:
                    tipo = 'Avanza1' if avanza(p) == q else 'Avanza2'
                    if q1 in ('1','8'): tipo = 'Promozione Avanza'
                    return True, tipo
        lato = right if right(p) != None and qa == right(p)[0] else False
        if not lato: lato = left if left(p) != None and qa == left(p)[0] else False
        if lato:
            # Provo a mangiare
            if lato(avanza(p)) == q: 
                # Provo a mangiare Normale
                if mangiato != None: 
                    sposta(partita.scacchiera, mossa)
                    sottoScacco = partita.sonoSottoScacco()
                    sposta(partita.scacchiera, q+p)
                    partita.scacchiera.pezzi[q] = mangiato
                    if not sottoScacco:
                        tipo = 'Promozione Mangia' if q1 in ('1','8') else 'Pedone Mangia'
                        return True, tipo
                else:
                    mangiatoEnpassant = partita.scacchiera.getPezzo(lato(p))
                    # Provo a mangiare Enpassant
                    if mangiatoEnpassant != None: 
                        if mangiatoEnpassant.nome == 'PEDONE' and mangiatoEnpassant.colore != pezzo.colore: 
                            if mangiatoEnpassant.appenaMossoDoppio == True:
                                sposta(partita.scacchiera, mossa)
                                del partita.scacchiera.pezzi[lato(p)]
                                sottoScacco = partita.sonoSottoScacco()
                                sposta(partita.scacchiera, q+p)
                                partita.scacchiera.pezzi[lato(p)] = mangiatoEnpassant
                                if not sottoScacco:
                                    return True, 'Enpassant'
    return False, None

def mlRe(partita, mossa):
    pa, p1, qa, q1 = mossa; p = pa+p1;
    re = partita.scacchiera.getPezzo(p)
    # Provo Mossa Normale
    ok, tipoMossa = noSpeciali(partita, mossa, reAttacca)
    if ok:
        return True, tipoMossa
    # Provo ad arroccare
    i = '1' if re.colore == BIANCO else '8' # Riga dell'arrocco
    if mossa == 'e'+i+'c'+i or mossa == 'e'+i+'g'+i:
        torre = partita.scacchiera.getPezzo('a'+i) # Arrocco Lungo
        if mossa == 'e'+i+'g'+i: torre = partita.scacchiera.getPezzo('h'+i) # Arrocco Corto
        c1 = torre != None and torre.colore == re.colore and torre.nome == 'TORRE'
        if c1:
            c2 = not torre.mosso() and not re.mosso()
            if c2:
                if mossa == 'e'+i+'c'+i: # Arrocco Lungo:
                    c3 = partita.scacchiera.getPezzo('b'+i) == None
                    c3 = partita.scacchiera.getPezzo('c'+i) == None and c3
                    c3 = partita.scacchiera.getPezzo('d'+i) == None and c3
                else: # Arrocco Corto:
                    c3 = partita.scacchiera.getPezzo('f'+i) == None
                    c3 = partita.scacchiera.getPezzo('g'+i) == None and c3
                if c3:
                    c4 = not partita.sonoSottoScacco()
                    if c4:
                        c5 = True
                        pezzi = partita.scacchiera.getNeri() if re.colore == BIANCO else partita.scacchiera.getBianchi()
                        posizioni = ['d'+i, 'c'+i] # Arrocco Lungo
                        if mossa == 'e'+i+'g'+i: posizioni = ['f'+i, 'g'+i] # Arrocco corto
                        for pezzo in pezzi:
                            if pezzo.attacca(partita.scacchiera, posizioni[0]) or pezzo.attacca(partita.scacchiera, posizioni[1]):
                                c5 = False; break;
                        if c5:
                            tipo = 'Arrocco Corto' if mossa == 'e'+i+'g'+i else 'Arrocco Lungo'
                            return True, tipo
    return False, None
    
# Altre funzioni

def sposta(scacchiera, mossa):
    p, q = (mossa[:2], mossa[2:])
    pezzo = scacchiera.getPezzo(p)
    scacchiera.pezzi[q] = pezzo
    del scacchiera.pezzi[p]
        
def eseguiMossa(partita, mossa, tipoMossa):
    p, q = mossa[:2], mossa[2:]
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
        s.pezzi[q] = Regina(q, colore, pezzo.storiaPosizioni)
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
                    if not pezzo1.mosso() == pezzo2.mosso():
                        return False
                # Controlla possibiltà di enpassant
    return True
    
def randomAI(partita):
    mosse = partita.mossePossibili()
    #mosse.append('back')
    n = len(mosse)
    if n == 0:
        return 'a1a1'
    i = rn.randint(0,n-1)
    return mosse[i]

def makeStats(nome = 'stats.txt', biancoAI = lambda p: randomAI(p), neroAI = lambda p: randomAI(p), n = 1000, stampaScacchiera = False):
    t = time.time()
    Finali = []
    contaMosse = {}
    for tipo in tipiMosse:
        contaMosse[tipo] = 0
    esiti = {'STALLO.':0, 'PATTA per 50 mosse senza mangiare.':0, 
             'PATTA per ripetizione.':0, 'Vince il BIANCO.':0, 
             'Vince il NERO.':0, 'NESSUNO':0}
    for i in tqdm(range(n)):
        game = Partita(mode = '0p', stampa = False, biancoAI = biancoAI, neroAI = neroAI)
        game.gioca()
        Finali.append({'Scacchiera': game.storiaConfigurazioni[-1], 
                       'Esito': game.esito,
                       'Mosse': len(game.mosse),
                       'Tempo': game.getTempoTot(BIANCO) + game.getTempoTot(NERO)})
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
        file.write('\n\t'+tipoMossa+':'+(' '*(20-len(tipoMossa)))+str(contaMosse[tipoMossa])+' volte')
    file.write('\n\tIndietro:            '+str(indietro)+' volte')
    file.write('\n\nOccorrenze esiti.\n')
    for esito in esiti:
        file.write('\n\t'+esito+':'+(' '*(40-len(esito)))+str(esiti[esito])+' volte')
    dt = time.time() - t
    file.write('\n\nTempi.\n')
    file.write('\n\tCopia:             ' + str(tCopia) + ' s')
    file.write('\n\tInit Scacchiera:   ' + str(tInitScacchiera) + ' s')
    file.write('\n\tIndietro:          ' + str(tIndietro) + ' s')
    file.write('\n\tTotale:            ' + str(dt) + ' s')
    file.write('\n\nMedia Velocità:        ' + str(int((n / dt) * 100)/100) + ' it/s')
    file.close()
    
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

#makeStats('faivedereapapa.txt', n = 100)

#s = Scacchiera()
#print(s)
#t = Scacchiera(s.pezzi)

#game = Partita(mode = '0p')
#game.gioca()

#game = Partita(mode = '1p')
#game.gioca()

#game = Partita(mode = '2p')
#game.gioca()

#game = Partita(mode = 'listaMosse')
#game.gioca(['e2e4', 'e7e5', 'f1c4', 'f8c5', 'g1f3', 'g8f6'])
#game.mossePossibili()
    
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
#game.salva('partitaRandom4.txt')

#for i in tqdm(range(25)):
#    game = Partita(mode = '0p', stampa = False)
#    game.gioca()

#game = Partita.carica('partitaRandom4.txt')
    
###############################################################################
#                                                                             #
#   Commenti per idee e memo                                                  #
#                                                                             #
############################################################################### 
    
# Aggiunta la possibilità di caricare una partita salvata.
# Risolto il problema che 'Avanza2' potesse saltare i pezzi.
# Risolto il problema che 'Pedone Mangia' non azzerava il conto delle mosse.
# senza mangiare.
# Aggiunto il metodo 'indietro'
# Trasformato in funzione il makeStats e mglioratone il funzionamento.
# Risolto il problema dell'arrocco che non veniva tornato come mossa possibile.
#
# Aggiungi modo per passare dalla notazione algebrica a quella completa e 
# viceversa.
#
# Scrivi i setCampo e i getCampo
#
# storiaConfigurazioni copia ogni volta la scacchiera: è lento (ma manco 
# troppo in realtà).
#
# Forse il metodo indietro potrebbe sfruttare più il salvataggio di 
# storiaConfigurazoni.
#
# Pareggi:
#   Differenziare tra pareggio proposto e obbligato
#   Pareggio per ripetizione:
#       controlla possibilità di enpassant
#

tTot = time.time() - tTot
print('\n...Esecuzione in '+str(int(tTot*1000)/1000) + ' secondi.')