# coding=utf-8
#
# Projet MOGPL 2015-2016
#
# problem.py
# Logique et représentation des problèmes de robot
#

from tools import *
from random import randint


class Problem:
    """
    Le problème du robot.

    @attr size: tuple (int, int) décrivant la taille de la grille du probleme
    @attr start: tuple (int, int, orientation) - coordonnées de départ du robot
    @attr obj:  tuple (int, int) - coordonnées objectives du robot
    @attr matrix: grille du problème
    """
    def __init__(self, size, start, obj, matrix):
        self.size = size
        self.start = start
        self.obj = obj
        self.matrix = matrix

    def __str__(self):
        res = "Taille de grille: " + str(self.size) + "\n"
        res += "Position de départ: " + str(self.start[0:2]) + "\n"
        res += "Orientation de départ: " + str(self.start[2]) + "\n"
        res += "Objectif: " + str(self.obj) + "\n"
        res += "Grille: \n"
        for line in self.matrix:
            res += "[ "
            for j in line: 
                if j == 1:
                    res += TCol.RE + "X" + TCol.ST + ", "
                else:
                    res += TCol.GR + str(j) + TCol.ST + ", "
            res += "\b\b ]\n"
        return res

    def getMatrix(self):
        return self.matrix

    def getStart(self):
        return self.start

    def getFinish(self):
        return self.obj

    @staticmethod
    def parseProblems(problemFile):
        problems = {}
        for f in problemFile:
            problems[f] = []
            for p in problemFile[f]:
                problems[f].append(Problem(*p))
        return problems

    @staticmethod
    def generate(h, w, pctObs):
        """
        Génère une instance aléatoire de Problem

        @param h: hauteur de la grille problème
        @param w: largeur de la grille problème
        @param pctObs: pctage d'observeurs requis
        """
        matrix = genererMatriceRect(h, w, pctObs)
        startx, starty, objx, objy = 0, 0, 0, 0
        while True:
            startx = randint(0, h-1)
            starty = randint(0, w-1)
            if startx < len(matrix) and starty < len(matrix[0]):
                if matrix[startx][starty] == 1:
                    continue
            if 0 <= startx - 1 < len(matrix) and starty < len(matrix[0]):
                if matrix[startx - 1][starty] == 1:
                    continue
            if startx < len(matrix) and 0 <= starty - 1 < len(matrix[0]):
                if matrix[startx][starty-1] == 1:
                    continue
            if 0 <= startx - 1 < len(matrix) and 0 <= starty - 1 < len(matrix[0]):
                if matrix[startx - 1][starty - 1] == 1:
                    continue
            break
        while True:
            objx = randint(0, h-1)
            objy = randint(0, w-1)
            if objx < len(matrix) and objy < len(matrix[0]):
                if matrix[objx][objy] == 1:
                    continue
            if 0 <= objx - 1 < len(matrix) and objy < len(matrix[0]):
                if matrix[objx - 1][objy] == 1:
                    continue
            if objx < len(matrix) and 0 <= objy - 1 < len(matrix[0]):
                if matrix[objx][objy-1] == 1:
                    continue
            if 0 <= objx - 1 < len(matrix) and 0 <= objy - 1 < len(matrix[0]):
                if matrix[objx - 1][objy - 1] == 1:
                    continue
            break
        orientation = Orientation(randint(0, 3))
        return Problem((h, w),
                       (startx, starty, orientation),
                       (objx, objy), matrix)

    @staticmethod
    def generateSquare(taille, nbObs):
        """
        Génère une instance aléatoire de Problem

        @param taille: largeur et hauteur de la grille problème
        @param nbObs: nombre d'observeurs requis
        """
        return Problem.generate(taille, taille, nbObs)

    @staticmethod
    def ListToString(probList):
        res = ""
        for p in probList:
            res += p.fileString() + "\n\n"
        return res

    def fileString(self):
        problem = "{} {}\n".format(self.size[0], self.size[1])
        for line in self.matrix:
            for i in line:
                problem += "%d " % i
            problem += "\n"
        problem += "{} {} {} {} {}\n".format(self.start[0],
                                             self.start[1],
                                             self.obj[0],
                                             self.obj[1],
                                             self.start[2].name)
        return problem

    def solve(self):
        """
        Résoud le problème de plus court chemin du robot

        @return: la liste de noeuds du plus court chemin
        """
        # Créer la matrice des noeuds
        railMatrix = RailMatrix(self.matrix)
        railMatrix.fillNodes()
        # Définir premier et dernier noeuds
        startX, startY, orientation = self.start
        Node.set(railMatrix)
        startNodes = railMatrix.getNodes(startX, startY)
        stopNodes = railMatrix.getNodes(*self.obj)
        # Position de départ/arrivée illégale
        if startNodes is None or stopNodes is None:
            return None
        startNode = railMatrix.getNode(startX, startY, orientation)
        startNode.setMark()
        Node.setStartingCost(startNodes, startNode, orientation)
        for n in startNodes:
            railMatrix.addNodeBorder(n)
        # Boucle Dijkstra
        while not(stopNodes[0].isMarked() and stopNodes[1].isMarked() and
            stopNodes[2].isMarked() and stopNodes[3].isMarked()) and not railMatrix.emptyBorder():
            curNode = railMatrix.getBorderMin()
            curNode.updateNeighbours()
        # Examen de la matrice complétée
        targetNode = stopNodes[0]
        minCost = targetNode.getCost()
        for n in stopNodes:
            if n.getCost() != -1 and (minCost == -1 or n.getCost() < minCost):
                minCost = n.getCost()
                targetNode = n
        # Retourne la solution
        listNode = targetNode
        solutionList = []
        while not listNode.getMinParent() is None:
            solutionList.append(listNode)
            listNode = listNode.getMinParent()
        solutionList.append(startNode)
        return solutionList

    @staticmethod
    def solutionString(solutionList):
        if solutionList is None:
            return "0 "
        curNode = solutionList.pop()
        res = ""
        while len(solutionList) > 0:
            nextNode = solutionList.pop()
            # Changement d'orientation
            or1 = nextNode.getOr()
            or2 = curNode.getOr()
            if not Orientation.isSame(or1, or2):
                if Orientation.isRight(or1, or2):
                    res += "D "
                elif Orientation.isLeft(or1, or2):
                    res += "G "
                else:
                    res += "G G "
            # Changement de position
            xcur, ycur = curNode.getPos()
            xnext, ynext = nextNode.getPos()
            if xcur == xnext and ycur != ynext:
                res += "a{} ".format(abs(ycur - ynext))
            elif ycur == ynext and xcur != xnext:
                res += "a{} ".format(abs(xcur - xnext))
            curNode = nextNode
        return "{} {}".format(curNode.getCost(), res)


class RailMatrix:
    """
    La matrice des noeuds accessibles/inaccessibles du graphe.
         - Contient 4 noeuds par position (N, S, O, E)
         - Est différente de la matrice lue dans le fichier
    """

    def __init__(self, problemMatrix):
        self.height = len(problemMatrix) + 1
        self.width = len(problemMatrix[0]) + 1
        self.problemMatrix = problemMatrix
        self.border = MyHeap()
        self.rails = []
        for i in range(self.height):
            line = []
            for j in range(self.width):
                line.append(None)
            self.rails.append(line)

    def __str__(self):
        res = ""
        for i in range(self.height):
            res += "{} ".format(i)
            for j in range(self.width):
                res += "("
                for d in Orientation:
                    if self.getNode(i, j, d) is None:
                        res += "{}, ".format("X")
                    else:
                        res += "{}:{},".format(d.name, self.getNode(i, j, d).getCost())
                res += ")"
            res += "\n"
        return res

    def fillNodes(self):
        for i in range(self.height):
            for j in range(self.width):
                # Case problemMatrix occupée par un obstacle:
                if i < len(self.problemMatrix) and j < len(self.problemMatrix[0]):
                    if self.problemMatrix[i][j] == 1:
                        self.rails[i][j] = None
                        continue
                if 0 <= i - 1 < len(self.problemMatrix) and j < len(self.problemMatrix[0]):
                    if self.problemMatrix[i-1][j] == 1:
                        self.rails[i][j] = None
                        continue
                if i < len(self.problemMatrix) and 0 <= j - 1 < len(self.problemMatrix[0]):
                    if self.problemMatrix[i][j-1] == 1:
                        self.rails[i][j] = None
                        continue
                if 0 <= i - 1 < len(self.problemMatrix) and 0 <= j - 1 < len(self.problemMatrix[0]):
                    if self.problemMatrix[i-1][j-1] == 1:
                        self.rails[i][j] = None
                        continue
                # intersection réalisable
                self.rails[i][j] = {}
                for direction in Orientation:
                    self.rails[i][j][direction.name] = Node(i, j, direction)

    def getNode(self, x, y, direction):
        if not self.rails[x][y] is None:
            return self.rails[x][y][direction.name]
        else:
            return None

    def getNodes(self, x, y):
        if self.rails[x][y] is None:
            return None
        ret = []
        for d in Orientation:
            ret.append(self.getNode(x, y, d))
        return ret

    def addNodeBorder(self, node):
        self.border.push(node)

    def getBorderMin(self):
        return self.border.pop()

    def emptyBorder(self):
        return self.border.isEmpty()

    def getH(self):
        return len(self.rails)

    def getW(self):
        return len(self.rails[0])


class Node:
    """
    Un noeud du graphe représentant le problème

    @param nodeX, nodeY: position du noeud dans la grille
    @param orientation: l'orientation du robot s'il choisit ce noeud
    """
    height = 0
    width = 0
    rails = None

    def __init__(self, nodeX, nodeY, orientation):
        self.cost = -1
        self.mark = False
        self.nodeX = nodeX
        self.nodeY = nodeY
        self.orientation = orientation
        self.minParent = None

    def __lt__(self, other):
        return self.cost <= other.getCost()

    def __str__(self):
        return "x:{} y:{} cost:{}".format(self.nodeX, self.nodeY, self.cost)

    @staticmethod
    def set(rails):
        Node.height = rails.getH()
        Node.width = rails.getW()
        Node.rails = rails

    @staticmethod
    def setStartingCost(nodeList, origin, orientation):
        for n in nodeList:
            if Orientation.isSame(orientation, n.getOr()):
                n.setCost(0)
            elif Orientation.isOpposite(orientation, n.getOr()):
                n.setCost(2)
                n.setMinParent(origin)
            else:
                n.setCost(1)
                n.setMinParent(origin)

    def getPos(self):
        return self.nodeX, self.nodeY

    def getOr(self):
        return self.orientation

    def getCost(self):
        return self.cost

    def setCost(self, cost):
        self.cost = cost

    def setMark(self):
        self.mark = True

    def isMarked(self):
        return self.mark

    def setMinParent(self, parent):
        self.minParent = parent

    def getMinParent(self):
        return self.minParent

    def updateNeighbours(self):
        """
        Voisins: 3 dans chaque direction.
        Selon la direction du noeud, le cout pour les
        atteindre est soit 1, soit 2
        """
        if self.isMarked():
            return
        for d in Orientation:
            # Calculs incréments
            if Orientation.isSame(d, self.orientation):
                incr = 1
            elif Orientation.isOpposite(d, self.orientation):
                incr = 3
            else:
                incr = 2
            # Calculs pas (1, 2 ou 3 pas d'un coup)
            for i in [1, 2, 3]:
                newX, newY = Orientation.move(d, self.nodeX, self.nodeY, i)
                # Out of range?
                if newX < 0 or newX >= Node.height \
                        or newY < 0 or newY >= Node.width:
                    break
                tempNode = self.rails.getNode(newX, newY, d)
                # Obstacle sur le chemin?
                if tempNode is None:
                    break
                # Noeud marqué?
                if tempNode.isMarked():
                    continue
                self.rails.addNodeBorder(tempNode)
                newCost = self.getCost() + incr
                # Cout amélioré Min Bordure amélioré?
                if tempNode.getCost() == -1 or tempNode.getCost() >= newCost:
                    tempNode.setCost(newCost)
                    tempNode.setMinParent(self)
        # Tous voisins visités
        self.setMark()
