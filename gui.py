# coding=utf-8
#
# Projet MOGPL 2015-2016
#
# gui.py
# Composants PyQt standalone sans logique
#
from sympy.vector import orienters

from tools import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *


class QProblemWindow(QWidget):
    """
    QProblemWindow: 
    Le widget contenant la grille de boutons.
    La résolution du problème se fait à partir de cette grille.

    @attr matrix:    la matrice représentant le problème 
    @attr start:     le départ
    @attr finish:    l'objectif du problème
    @attr step:      la taille actuelle d'un QSquare individuel
    @attr defStart:  booléen pour la définition d'un nouveau départ
    @attr defFinish: booléen pour la définition d'un nouvel objectif
    """
    def __init__(self, problem):

        super(QProblemWindow, self).__init__()
        # Widgets
        self.problem = problem
        self.start = problem.getStart()
        self.finish = problem.getFinish()
        self.matrix = problem.getMatrix()
        self.step = int(min(self.size().height()/len(self.matrix),
                            self.size().width()/len(self.matrix[0])))
        # Grid
        for i in range(len(self.matrix)):
            for j in range(len(self.matrix[0])):
                button = QSquare(self, i, j, self.matrix[i][j] == 1)
                button.setStyle()
                button.setGeometry(self.step*j, self.step*i, self.step, self.step)
                button.setParent(self)
        # Defining new start/finish
        self.defStart = False
        self.defFinish = False

    def isDefStart(self):
        return self.defStart

    def setDefStart(self, b):
        self.defStart = b
    
    def isDefFinish(self):
        return self.defFinish

    def setDefFinish(self, b):
        self.defFinish = b
    
    def getProblem(self):
        return self.problem

    def getMatrix(self):
        return self.matrix

    def getStart(self):
        return self.start

    def setStart(self, start):
        self.start = start

    def getFinish(self):
        return self.finish

    def setFinish(self, finish):
        self.finish = finish

    def checkAround(self, h, w):
        """
        Vérifie les cases autour de matrix[h, w] pour vérifier si le rail est 
        disponible
        """
        maxh = len(self.matrix)
        maxw = len(self.matrix[0])
        if 0 <= h < maxh and 0 <= w < maxw :      # bd
            if self.matrix[h][w] == 1:
                return False
        if 0 <= h < maxh and 0 <= w-1 < maxw :    # bg
            if self.matrix[h][w-1] == 1:
                return False
        if 0 <= h-1 < maxh and 0 <= w < maxw :    # hd
            if self.matrix[h-1][w] == 1:
                return False
        if 0 <= h-1 < maxh and 0 <= w-1 < maxw :    # hg
            if self.matrix[h-1][w-1] == 1:
                return False
        return True
    
    def drawSol(self, mvStr):
        self.emit(SIGNAL("clearEdges()"))
        mvList = mvStr.split()
        mvList = mvList[::-1]
        hac, wac, orac = self.start
        hs, ws = self.finish
        mvList.pop()
        while len(mvList) != 0:
            mv = mvList.pop()
            if mv == "G":
                orac = Orientation((orac.value - 1)% 4)
            if mv == "D":
                orac = Orientation((orac.value + 1)% 4)
            if len(mv) == 2 and mv[0] == "a":
                step = int(mv[1])
                for i in range(step):
                    if orac.value == 0:
                        self.emit(SIGNAL("up(int, int)"), hac, wac)
                        self.emit(SIGNAL("down(int, int)"), hac-1, wac)
                        hac -= 1
                    elif orac.value == 1:
                        self.emit(SIGNAL("right(int, int)"), hac, wac)
                        self.emit(SIGNAL("left(int, int)"), hac, wac+1)
                        wac += 1
                    elif orac.value == 2:
                        self.emit(SIGNAL("down(int, int)"), hac, wac)
                        self.emit(SIGNAL("up(int, int)"), hac+1, wac)
                        hac += 1
                    else:
                        self.emit(SIGNAL("left(int, int)"), hac, wac)
                        self.emit(SIGNAL("right(int, int)"), hac, wac-1)
                        wac -= 1
                        
    def toggleSquare(self, x, y):
        self.matrix[x][y] = (self.matrix[x][y] + 1) % 2
        
    def resizeEvent(self, event):
        h = event.size().height()
        w = event.size().width()
        self.step = int(min(h/len(self.matrix), w/len(self.matrix[0])))
        if self.step == 0:
            self.step = 1
        self.emit(SIGNAL("resizeSq(int)"), self.step)
        self.emit(SIGNAL("resizeOb(int)"), self.step/4)


class QSquare(QPushButton):

    """
    QSquare: un élément de la grille.
    
    @attr x: position hauteur dans la grille problème
    @attr y: position largeur dans la grille problème
    @attr obstacle: booléen True si (x,y) est un obstacle
    """

    def __init__(self, p, x, y, obstacle):
        super(QSquare, self).__init__(parent=p)
        self.x = x
        self.y = y
        self.obstacle = obstacle

        # Init graphique
        self.setAutoFillBackground(True)
        self.drawFinish()
        self.drawStart()
        # Connexions
        #self.connect(self, SIGNAL("clicked()"), self.toggleObs)
        self.connect(self, SIGNAL("toggleSignal(int, int)"),
                     self.parent().toggleSquare)
        self.connect(self.parent(), SIGNAL("resizeSq(int)"), self.resizeSq)
        self.connect(self.parent(), SIGNAL("drawStart()"), self.drawStart)
        self.connect(self.parent(), SIGNAL("drawFinish()"), self.drawFinish)
        self.connect(self.parent(), SIGNAL("clearEdges()"), self.clearEdges)
        self.connect(self.parent(), SIGNAL("up(int, int)"), self.up)
        self.connect(self.parent(), SIGNAL("right(int, int)"), self.right)
        self.connect(self.parent(), SIGNAL("down(int, int)"), self.down)
        self.connect(self.parent(), SIGNAL("left(int, int)"), self.left)
        
    def drawStart(self):
        """
        Dessin du départ en vérifiant si self encadre la position de départ
        Dépend du start défini dans QProblemWindow
        """
        startx, starty, ori = self.parent().getStart()
        orientation = Orientation(ori)
        if startx == self.x and starty == self.y:              # draw haut gauche
            self.setIcon(QIcon("resources/hg.png"))
            self.connect(self.parent(), SIGNAL("clearStart()"), self.clearStart)
        elif startx == self.x and starty == self.y + 1:        # draw haut droite
            self.setIcon(QIcon("resources/hd.png"))
            self.connect(self.parent(), SIGNAL("clearStart()"), self.clearStart)
        elif startx == self.x + 1 and starty == self.y:        # draw bas gauche
            self.setIcon(QIcon("resources/bg.png"))
            self.connect(self.parent(), SIGNAL("clearStart()"), self.clearStart)
        elif startx == self.x + 1 and starty == self.y + 1:    # draw bas droite
            self.setIcon(QIcon("resources/bd.png"))
            self.connect(self.parent(), SIGNAL("clearStart()"), self.clearStart)
        self.setIconSize(QSize(self.width(), self.height()))
        # Dessiner l'orientation
        if Orientation.isSame(orientation, Orientation.nord):       # bg, bd
            if startx == self.x + 1 and starty == self.y:
                self.setIcon(QIcon("resources/bgau.png"))
            if startx == self.x + 1 and starty == self.y + 1:
                self.setIcon(QIcon("resources/bdau.png"))
        elif Orientation.isSame(orientation, Orientation.est):      # hg, bg
            if startx == self.x and starty == self.y:
                self.setIcon(QIcon("resources/hgar.png"))
            if startx == self.x + 1 and starty == self.y:
                self.setIcon(QIcon("resources/bgar.png"))
        elif Orientation.isSame(orientation, Orientation.sud):      # hg, hd
            if startx == self.x and starty == self.y:
                self.setIcon(QIcon("resources/hgad.png"))
            if startx == self.x and starty == self.y + 1:
                self.setIcon(QIcon("resources/hdad.png"))
        elif Orientation.isSame(orientation, Orientation.ouest):    # hd, bd
            if startx == self.x and starty == self.y + 1:
                self.setIcon(QIcon("resources/hdal.png"))
            if startx == self.x + 1 and starty == self.y + 1:
                self.setIcon(QIcon("resources/bdal.png"))

    def drawFinish(self):
        """
        Dessin de l'arrivée en vérifiant si self encadre la position objectif
        Dépend de l'arrivée définie dans QProblemWindow
        """
        # Dessiner le point:
        objx, objy = self.parent().getFinish()
        if objx == self.x and objy == self.y:              # draw haut gauche
            self.setIcon(QIcon("resources/hg.png"))
            self.connect(self.parent(), SIGNAL("clearFinish()"), self.clearFinish)
        elif objx == self.x and objy == self.y + 1:        # draw bas gauche
            self.setIcon(QIcon("resources/hd.png"))
            self.connect(self.parent(), SIGNAL("clearFinish()"), self.clearFinish)
        elif objx == self.x + 1 and objy == self.y:        # draw haut droite
            self.setIcon(QIcon("resources/bg.png"))
            self.connect(self.parent(), SIGNAL("clearFinish()"), self.clearFinish)
        elif objx == self.x + 1 and objy == self.y + 1:    # draw bas droite
            self.setIcon(QIcon("resources/bd.png"))
            self.connect(self.parent(), SIGNAL("clearFinish()"), self.clearFinish)
        self.setIconSize(QSize(self.width(), self.height()))        
        
    def clearStart(self):
        self.setIcon(QIcon())
        self.disconnect(self, SIGNAL("clearStart()"), self.clearStart)

    def clearFinish(self):
        self.setIcon(QIcon())
        self.parent().disconnect(self, SIGNAL("clearFinish()"), self.clearFinish)

    def clearEdges(self):
        self.setStyle()

    def setStyle(self):
        if self.obstacle:
            self.setStyleSheet("border-width: 1px; border-style: solid; border-color:#000000;" +
                               " background-color: #D09FE0")
        else:
            self.setStyleSheet("border-width: 1px; border-style: solid; border-color:#000000; background-color: white")
            
    def toggleObs(self):
        """
        Toggle si self est un obstacle.
        Impossible à modifier à obstacle = True si self encadre départ
        ou arrivée
        """
        startx, starty, orientation = self.parent().getStart()
        objx, objy = self.parent().getFinish()
        if not((startx == self.x and starty == self.y) or (startx == self.x and starty == self.y + 1) \
                or (startx == self.x + 1 and starty == self.y) or (startx == self.x + 1 and starty == self.y + 1) or
                   (objx == self.x and objy == self.y) or (objx == self.x and objy == self.y + 1) \
                or (objx == self.x + 1 and objy == self.y) or (objx == self.x + 1 and objy == self.y + 1)):
            self.obstacle = not self.obstacle
            self.setStyle()
            self.emit(SIGNAL("toggleSignal(int, int)"), self.x, self.y)

    def up(self, h, w):
        if h == self.x + 1 and w == self.y:
            ssh = self.styleSheet()
            ssh += "; border-left-color: #FF0000; border-left-width: 1px"
            self.setStyleSheet(ssh)

    def right(self, h, w):
        if h == self.x and w == self.y:
            ssh = self.styleSheet()
            ssh += "; border-top-color: #FF0000; border-top-width: 1px"
            self.setStyleSheet(ssh)
            
    def down(self, h, w):
        if h == self.x and w == self.y + 1:
            ssh = self.styleSheet()
            ssh += "; border-right-color: #FF0000; border-right-width: 1px"
            self.setStyleSheet(ssh)
            
    def left(self, h, w):
        if h == self.x + 1 and w == self.y + 1:
            ssh = self.styleSheet()
            ssh += "; border-bottom-color: #FF0000; border-bottom-width: 1px"
            self.setStyleSheet(ssh)
            
    def resizeSq(self, step):
        self.setGeometry(self.y*step, self.x*step, step, step)
        self.setIconSize(QSize(self.width(), self.height()))

    def mousePressEvent(self, event):
        # Coordonnées:
        x, y = event.x(), event.y()
        step = self.width()
        interw, interh = 0, 0
        if x < step/2 and y < step/2:        # hg
            interw, interh = self.y, self.x
        elif x > step/2 and y < step/2:      # hd
            interw, interh = self.y + 1, self.x
        elif x < step/2 and y > step/2:      # bg
            interw, interh = self.y, self.x + 1
        elif x > step/2 and y > step/2:      # bd
            interw, interh = self.y + 1, self.x + 1
        else:
            return
        if self.parent().isDefStart():
            if self.parent().checkAround(interh, interw):
                cpanel = self.parent().parent().getCtrlPanel()
                orientation = cpanel.getOr()
                self.parent().setStart((interh, interw, orientation))
                self.parent().emit(SIGNAL("clearStart()"))
                self.parent().emit(SIGNAL("drawStart()"))
                self.parent().setDefStart(False)
                cpanel.toggleFinish()
                return
            else:
                self.setDefStart(False)
                return
        if self.parent().isDefFinish():
            # Coordonnées valides?
            if self.parent().checkAround(interh, interw):
                cpanel = self.parent().parent().getCtrlPanel()
                self.parent().setFinish((interh, interw))
                print(self.parent().getFinish())
                self.parent().emit(SIGNAL("clearFinish()"))
                self.parent().emit(SIGNAL("drawFinish()"))
                self.parent().setDefFinish(False)
                cpanel.toggleStart()
                return
            else:
                self.setDefFinish(False)
                return
        self.toggleObs()
            
