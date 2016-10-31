# coding=utf-8
#
# Projet MOGPL 2015-2016
#
# tools.py
# Définitions utiles
#

import os
import heapq
import matplotlib.pyplot as plt
import numpy as np
from random import randint
from enum import Enum


class TCol:
    """
    Classe pour les escape sequence de couleurs
    """

    B = '\033[1m'
    RB = '\033[21m'
    RE = '\033[91m'
    GR = '\033[92m'
    BL = '\033[94m'
    ST = '\033[0m'


class Orientation (Enum):
    """
    Enum pour les points cardinaux

    Tourner à droite: of = or+1 mod 4
    Tourner à gauche: of = or-1 mod 4
    """
    nord = 0
    est = 1
    sud = 2
    ouest = 3

    @staticmethod
    def move(d, h, w, n):
        if d == Orientation.nord:
            return h-n, w
        elif d == Orientation.est:
            return h, w+n
        elif d == Orientation.sud:
            return h+n, w
        else:
            return h, w-n

    @staticmethod
    def isRight(or1, or2):
        return (or2.value + 1) % 4 == or1.value

    @staticmethod
    def isLeft(or1, or2):
        return (or2.value - 1) % 4 == or1.value

    @staticmethod
    def isOpposite(or1, or2):
        return (or1.value + 2) % 4 == or2.value

    @staticmethod
    def isSame(or1, or2):
        return or1.value == or2.value


class MyHeap:
    """
    Tas min pour suivre le minimum de la bordure
    """

    def __init__(self):
        self.heap = []

    def __str__(self):
        return str(self.heap)

    def push(self, node):
        if node.getCost() != -1:
            heapq.heappush(self.heap, (node.getCost(), node))
        else:
            heapq.heappush(self.heap, (999, node))

    def pop(self):
        cost, node = heapq.heappop(self.heap)
        return node

    def isEmpty(self):
        return len(self.heap) == 0

    def len(self):
        return len(self.heap)

                    
def readFiles(fileList):
    """
    Lecture des fichiers passés en argument dans la liste

    @param fileList: une liste de chemins vers des fichiers
    @return: un dictionnaire associant un fichier à une liste de problèmes
    """
    files = {}
    # On traite tous les fichiers
    for argv in fileList:
        try:
            files[argv] = []
            myFile = open(argv, "r")
            line = myFile.readline().rstrip()
            # Lecture du fichier
            while not line == "0 0":
                matrix = []
                # On saute les lignes vides éventuelles
                while line == "":
                    line = myFile.readline().rstrip()
                if line == "0 0":
                    break
                # Lecture de la taille
                size = tuple(map(int, line.split()))
                nblignes = size[0]
                # Lecture du bloc d'obstacles (nblignes lignes)
                for i in range(nblignes):
                    line = myFile.readline().rstrip()
                    matrix.append(map(int, line.split()))
                # Lecture de l'obj et du départ
                linesplit = myFile.readline().split()
                startpos = map(int, linesplit[0:2])
                start = tuple(startpos) + (Orientation[linesplit[4]],)
                obj = tuple(map(int, linesplit[2:4]))
                # Terminé! Addition du problème à la liste
                files[argv].append([size, start, obj, matrix])
                line = myFile.readline().rstrip()
            # Fini, fermeture.
            myFile.close()
            success = TCol.GR + "Fichier "
            success += TCol.B + "%s" % argv + TCol.RB + " lu!" + TCol.ST
            print(success)
        except (IndexError, ValueError):
            err = TCol.RE
            err += "Erreur de lecture " + TCol.B + "%s" % argv
            err += TCol.RB + ": format incorrect." 
            err += TCol.ST
            print(err)
            files.pop(argv)
            next
        finally:
            myFile.close()
    # Fin lecture des fichiers en argument
    return files


def genererMatrice(taille, nbObs):
    return genererMatriceRect(taille, taille, nbObs)


def genererMatriceRect(h, w, nbObs):
    """
    Génère une liste de listes
    0 pour une case accessible
    1 pour un obstacle
    """
    matrix = []
    for i in range(h):
        line = []
        for j in range(w):
            line.append(0)
        matrix.append(line)
    for i in range(nbObs):
        while True:
            x = randint(0, h-1)
            y = randint(0, w-1)
            if matrix[x][y] != 1:
                matrix[x][y] = 1
                break
    return matrix


def writeFile(path, items, problems=False):
    """
    Ecriture dans un fichier

    @param path: le chemin vers le fichier
    @param items: le etxte à écrire dans le fichier
    """
    d = os.path.dirname(path) if not os.path.dirname(path) == "" else "./"
    if not os.path.exists(d):
        os.makedirs(d)
    myFile = open(path, 'w')
    myFile.write(items)
    if problems:
        myFile.write("0 0")
    myFile.close()
    return None


def makePlot(timesDict, xaxis, xlabel):
    x = []
    y = []
    for size in xaxis:
        x.append(size)
        y.append(np.mean(timesDict[size]))
    coeffs = np.polyfit(x, y, 2)
    f = np.poly1d(coeffs)
    x_new = np.linspace(x[0], x[-1])
    y_new = []
    for i in x_new:
        y_new.append(f(i))
    plt.plot(x, y, 'yo', x_new, y_new, '--')
    plt.ylabel(u"Temps d'exécution (secondes)")
    plt.xlabel(xlabel)
    plt.show()
    
