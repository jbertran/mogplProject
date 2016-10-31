#!/usr/bin/python
# coding=utf-8
#
# Projet MOGPL 2015-2016
#
# main.py
# Outils de lecture/écriture de fichier
# Résolution de problèmes de robot à partir de fichiers texte
#

import sys
import time
from robot import *
from problem import *
from argparse import ArgumentParser

def main():
    parser = ArgumentParser()
    parser.add_argument("-f", nargs="+", type=str, help="Lecture et résolution de fichiers problèmes")
    parser.add_argument("-g", action="store_true", default=False, help="Interface graphique")
    parser.add_argument("-test", action="store_true", default=False, help="Exécution d'un jeu de tests")
    parser.add_argument("-testsize", action="store_true", default=False, help="Génération et résolution d'instances de tailles différentes")
    parser.add_argument("-testobs", action="store_true", default=False, help="Génération et résolution d'instances de nombre d'obstacle différents")
    args = parser.parse_args()
    traiterOptions(args)

def traiterOptions(args):
    if args.test:
        tests()
    elif args.testsize:
        solveRandomWithSize()
    elif args.testobs:
        solveRandomWithObstacles()
    elif args.g:
        appExec()
    elif args.f is not None:
        problemes = Problem.parseProblems(readFiles(args.f))
        if problemes == {}:
            return
        for myfile in args.f:
            print("Résolution des problèmes de {}".format(myfile))
            for i in problemes[myfile]:
                print(Problem.solutionString(i.solve()))

def tests():
    # Test chargement de fichiers
    print("************************************************")
    print("*             Lecture de problèmes             *")
    print("************************************************")
    problemes = Problem.parseProblems(readFiles(["sample.pb"]))
    for f in problemes:
        print(f+":\n")
        for p in problemes[f]:
            print(str(p))
    # Génération de problèmes aléatoires
    sizes = [5 , 10, 15, 20]
    objRatio = 0.25
    print("************************************************")
    print("*             Problèmes aléatoires             *")
    print("************************************************")
    myProbs = []
    for i in sizes:
        myProbs.append(Problem.generateSquare(i, int(pow(i, 2) * objRatio)))
        for p in myProbs:
            print(p)
    # Ecriture dans fichiers
    print("************************************************")
    print("*            Vérification écriture             *")
    print("************************************************")
    path = "FichiersTest/fichierpb.pb"
    writeFile(path, Problem.ListToString(myProbs), True)
    res = Problem.parseProblems(readFiles([path]))
    for p in res["FichiersTest/fichierpb.pb"]:
        print(p)
    print("************************************************")
    print("*                   DIJKSTRA                   *")
    print("************************************************")
    spath = "FichiersTest/dijkstra.sol"
    listP = problemes["sample.pb"][2].solve()
    print("Chemin solution à partir de l'objectif: ")
    print([(n.getPos(), n.getOr().name) for n in listP])
    res = Problem.solutionString(listP)
    print(res)
    try:
        writeFile(spath, res)
        print(TCol.GR + "Ecriture solution: " + TCol.B + "OK" + TCol.ST)
    except KeyError:
        print(TCol.RE + "Ecriture solution: " + TCol.B + "échec" + TCol.ST)


def solveRandomWithSize():
    graphName = "Obstacles/obstaclesFixes.pdf"
    sizes = [10, 20, 30, 40, 50]
    nbInstances = 10
    myProbs = {}
    mySolutions = {}
    solvingTimes = {}
    for i in sizes:
        print("Matrices carrées aléatoires de taille {}: ".format(i))
        myProbs[i] = []
        mySolutions[i] = []
        solvingTimes[i] = []
        for nb in range(nbInstances):
            pb = Problem.generateSquare(i, int(i/4))
            myProbs[i].append(pb)
            # Begin timer
            t = time.time()
            s = Problem.solutionString(pb.solve())
            solvingTimes[i].append(time.time() - t)
            # End timer
            mySolutions[i].append(s)
            print("{}/{}...".format(nb+1, nbInstances))
        # Dump problems and solutions
        ppath = "FichiersPb/randomWithSizepbs{}.pb".format(i)
        spath = "FichiersPb/randomWithSizepbs{}.sol".format(i)
        writeFile(ppath, Problem.ListToString(myProbs[i]), True)
        sols = ""
        for s in mySolutions[i]:
            sols += "{}\n\n".format(s)
        writeFile(spath, sols)
        print("")
    for i in sizes:
        print("Instances de taille {}:".format(i))
        for s in mySolutions[i]:
            print(s)
    makePlot(solvingTimes, sizes, u"Taille de la matrice problème")


def solveRandomWithObstacles():
    nbObs = [10, 20, 30, 40, 50]
    msize = 20
    nbIter = 10
    myProbs = {}
    mySolutions = {}
    solvingTimes = {}
    for i in nbObs:
        print("Matrices carrées de taille 20 avec {} obstacles: ".format(i))
        myProbs[i] = []
        mySolutions[i] = []
        solvingTimes[i] = []
        for nb in range(nbIter):
            pb = Problem.generateSquare(20, i)
            myProbs[i].append(pb)
            # Begin timer
            t = time.time()
            s = Problem.solutionString(pb.solve())
            solvingTimes[i].append(time.time() - t)
            # End timer
            mySolutions[i].append(s)
            print("{}/{}...".format(nb+1, nbIter))
        # Dump problems and solutions
        ppath = "FichiersPb/randomWithObspbs{}.pb".format(i)
        spath = "FichiersPb/randomWithObspbs{}.sol".format(i)
        writeFile(ppath, Problem.ListToString(myProbs[i]), True)
        sols = ""
        for s in mySolutions[i]:
            sols += "{}\n\n".format(s)
        writeFile(spath, sols)
        print("")
    for i in nbObs:
        print("Instances de taille {}:".format(i))
        for s in mySolutions[i]:
            print(s)
    makePlot(solvingTimes, nbObs, "Nombre d'obstacles")

if __name__ == "__main__":
    main()

