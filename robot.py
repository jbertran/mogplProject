# coding=utf-8
#
# Projet MOGPL 2015-2016
#
# robot.py
# Interface graphique pour jouer avec le robot
#

import sys
from problem import *
from gui import *
from PyQt4.QtGui import *
from PyQt4.QtCore import *


class MyApp(QWidget):

    winit = 10
    hinit = 10
    oinit = 0
    
    def __init__(self):
        super(MyApp, self).__init__()
        self.problempanel = QProblemWindow(Problem.generate(MyApp.hinit, MyApp.winit, int(MyApp.winit*MyApp.hinit*MyApp.oinit)))
        self.controlpanel = QControlPanel(MyApp.winit, MyApp.hinit)
        self.solutionPanel = QTextEdit("")
        self.panels = QBoxLayout(QBoxLayout.LeftToRight)
        self.initUI()

    def initUI(self):
        self.problempanel.setMinimumWidth(400)
        self.problempanel.setParent(self)
        self.controlpanel.setMaximumWidth(170)
        self.controlpanel.setParent(self)
        self.solutionPanel.setMaximumWidth(200)
        self.solutionPanel.setReadOnly(True)

        solutionLayout = QBoxLayout(QBoxLayout.TopToBottom)
        solutionLayout.addWidget(QLabel("Solution:"))
        solutionLayout.addWidget(self.solutionPanel)
        self.panels.addLayout(solutionLayout)
        self.panels.addWidget(self.controlpanel)
        self.panels.addWidget(self.problempanel)
        self.setLayout(self.panels)
        self.setWindowTitle("La balade du robot")
        self.resize(500, 400)
        self.show()

    def setSolution(self, text):
        self.solutionPanel.setText(text)
        
    def getPanels(self):
        return self.panels

    def addWidgetPanels(self, widget):
        self.panels.addWidget(widget)

    def getCtrlPanel(self):
        return self.controlpanel

    def getPbPanel(self):
        return self.problempanel

    def setPb(self, pbPanel):
        pbPanel.setParent(self)
        self.panels.removeWidget(self.problempanel)
        self.problempanel.deleteLater()
        self.problempanel = pbPanel
        self.panels.addWidget(self.problempanel)
        self.problempanel.update()


class QControlPanel(QWidget):
    """
    QControlPanel: logique de l'application PyQt

    Contrôle les boutons du panneau de contrôle. Cf. gui.py pour l'affichage
    """

    def __init__(self, h, w):
        super(QControlPanel, self).__init__()
        self.buttons = QBoxLayout(QBoxLayout.TopToBottom)
        self.random = QPushButton(u"Problème Aléatoire")
        self.load = QPushButton("Charger")
        self.save = QPushButton("Sauvegarder")
        self.solve = QPushButton(u"Résoudre")
        self.depart = QPushButton(u"Départ")
        self.arrivee = QPushButton(u"Arrivée")
        self.wsl = QSlider(Qt.Horizontal, self)
        self.hsl = QSlider(Qt.Horizontal, self)
        self.nbObs = QSlider(Qt.Horizontal, self)
        self.orient = QComboBox(self)
        self.solArea = QTextEdit("Solution...")
        self.lw = QLabel("Largeur: {}".format(h))
        self.lh = QLabel("Hauteur: {}".format(w))
        self.lo = QLabel("Nombre d'obstacles: {}".format(MyApp.oinit))
        self.problemCBBox = QComboBox(self)
        self.problemList = None
        self.initUI()
        self.initLayout()
        self.connectStuff()

    def initUI(self):
        self.wsl.setRange(5, 60)
        self.wsl.setValue(MyApp.winit)
        self.hsl.setRange(5, 60)
        self.hsl.setValue(MyApp.hinit)
        self.nbObs.setRange(0, MyApp.winit*MyApp.hinit/2)
        self.nbObs.setValue(0)
        self.problemCBBox.hide()
        for i in range(4):
            self.orient.addItem("{}".format(Orientation(i).name).capitalize())
        
    def initLayout(self):
        init = QBoxLayout(QBoxLayout.LeftToRight)
        ori = QBoxLayout(QBoxLayout.TopToBottom)
        ori.addWidget(self.depart)
        ori.addWidget(self.orient)
        init.addLayout(ori)
        init.addWidget(self.arrivee)
        height = QBoxLayout(QBoxLayout.TopToBottom)
        height.addWidget(self.lh)
        height.addWidget(self.hsl)
        width = QBoxLayout(QBoxLayout.TopToBottom)
        width.addWidget(self.lw)
        width.addWidget(self.wsl)
        obsta = QBoxLayout(QBoxLayout.TopToBottom)
        obsta.addWidget(self.lo)
        obsta.addWidget(self.nbObs)

        self.buttons.addLayout(init)
        self.buttons.addLayout(height)
        self.buttons.addLayout(width)
        self.buttons.addLayout(obsta)
        self.buttons.addWidget(self.solve)
        self.buttons.addWidget(self.random)
        self.buttons.addWidget(self.load)
        self.buttons.addWidget(self.save)
        self.setLayout(self.buttons)

    def connectStuff(self):
        self.connect(self.hsl, SIGNAL("valueChanged(int)"), self.updateH)
        self.connect(self.wsl, SIGNAL("valueChanged(int)"), self.updateW)
        self.connect(self.nbObs, SIGNAL("valueChanged(int)"), self.updateO)
        self.connect(self.orient, SIGNAL("currentIndexChanged(int)"), self.updateOr)
        self.connect(self.load, SIGNAL("clicked()"), self.loadFile)
        self.connect(self.save, SIGNAL("clicked()"), self.saveFile)
        self.connect(self.solve, SIGNAL("clicked()"), self.solvePb)
        self.connect(self.random, SIGNAL("clicked()"), self.randomMatrix)
        self.connect(self.depart, SIGNAL("clicked()"), self.newDepart)
        self.connect(self.arrivee, SIGNAL("clicked()"), self.newArrivee)

    def getH(self):
        return self.hsl.value()

    def getW(self):
        return self.wsl.value()

    def getO(self):
        return self.osl.value()

    def getOr(self):
        return Orientation(self.orient.currentIndex())

    def updateW(self, w):
        self.lw.setText("Largeur: {}".format(w))
        self.nbObs.setRange(0, self.getH()*w - 8)

    def updateH(self, h):
        self.lh.setText("Hauteur: {}".format(h))
        self.nbObs.setRange(0, self.getW()*h - 8)

    def updateO(self, o):
        self.lo.setText("Nombre d'obstacles: {}".format(o))

    def clearCBox(self):
        self.problemCBBox.hide()

    def updateOr(self, o):
        pb = self.parent().getPbPanel()
        x, y, orient = pb.getStart()
        pb.setStart((x, y, Orientation(o)))
        pb.emit(SIGNAL("clearStart()"))
        pb.emit(SIGNAL("drawStart()"))
       
    def toggleStart(self):
        if self.depart.isEnabled():
            self.depart.setDisabled(True)
        else:
            self.depart.setDisabled(False)
        
    def toggleFinish(self):
        if self.arrivee.isEnabled():
            self.arrivee.setDisabled(True)
        else:
            self.arrivee.setDisabled(False)
        
    def loadFile(self):
        print("Charger?")
        fileName = str(QFileDialog(self).getOpenFileName(self, "Ouvrir", "."))
        if fileName != "":
            problemDict = Problem.parseProblems(readFiles([fileName]))
            if problemDict == {}:
                return
            self.problemList = problemDict[fileName]
            self.problemCBBox = QComboBox(self)
            self.buttons.addWidget(self.problemCBBox)
            self.problemCBBox.addItem("")
            for p in range(len(self.problemList)):
                self.problemCBBox.addItem(u"Pb. {}".format(p+1))
                self.connect(self.problemCBBox, SIGNAL("currentIndexChanged(int)"), self.onChanged)
            self.problemCBBox.show()

    def onChanged(self, index):
        if index > 0:
            print("Changement de problème:")
            problem = self.problemList[index-1]
            print(self.problemList[index-1])
            self.orient.setCurrentIndex(problem.getStart()[2].value)
            self.parent().setPb(QProblemWindow(self.problemList[index-1]))

    def saveFile(self):
        print("Save?")
        pbpane = self.parent().getPbPanel()
        problem = Problem((self.getH(), self.getW()),
                          pbpane.getStart(),
                          pbpane.getFinish(),
                          pbpane.getMatrix())
        saveFile = str(QFileDialog(self).getSaveFileName(self, "Sauvegarder"))
        if saveFile != "":
            writeFile(saveFile, problem.fileString(), problems=True)

    def solvePb(self):
        print("Solving...")
        pbpane = self.parent().getPbPanel()
        print(pbpane.getProblem())
        self.parent().setSolution(u"En cours de résolution...")
        problem = Problem((self.getH(), self.getW()), pbpane.getStart(), pbpane.getFinish(), pbpane.getMatrix())
        sol = Problem.solutionString(problem.solve())
        print("Solved!")
        self.parent().setSolution(sol if sol != "0 " else "Pas de solution!")
        if sol != "0 ":
            pbpane.drawSol(sol)

    def randomMatrix(self):
        self.clearCBox()
        print("Random matrix")
        p = Problem.generate(self.hsl.value(), self.wsl.value(), self.nbObs.value())
        index = p.getStart()[2].value
        self.orient.setCurrentIndex(index)
        newpPanel = QProblemWindow(p)
        self.parent().setPb(newpPanel)

    def newArrivee(self):
        self.parent().getPbPanel().setDefFinish(True)
        self.depart.setDisabled(True)
        
    def newDepart(self):
        self.parent().getPbPanel().setDefStart(True)
        self.arrivee.setDisabled(True)

def appExec():
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("resources/icon.png"))
    appW = MyApp()
    sys.exit(app.exec_())
