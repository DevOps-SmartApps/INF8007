#!/usr/bin/python3

import re
import sys
import os
import glob
import numpy as np
from collections import *
from nltk.stem.snowball import SnowballStemmer
from scipy.sparse import csr_matrix
from tqdm import tqdm
#python pickle

def prepMatrix(n,d):
    for j in tqdm(range(0,d), "Matrix preparation"):
        for key in bigListD[j]:
            Mdata.append(bigListD[j][key])
            Mrow.append(dictIndex[key])
            #Mrow.append(bigListW.index(key))
        for i in range(0,len(bigListD[j])):
            Mcol.append(j)


        #for key in bigListD[j]:
            #matrix[bigListW.index(key),j]=bigListD[j][key]
            #print(bigListW.index(key))
            #scipyparse needed here

def wordSep(content):
    dict_words = {}
    regex_word = r'\W+'
    regex_space = r'\s'
    regex_des = 'DescriptionCours'

    CleanString = re.sub('\W+',' ',content) # Ajoute d'un espace avant les points

    #Remplacer par racine et enlever mots inutiles
    courseDesc = re.split(regex_des,CleanString)
    words = re.split(regex_word,courseDesc[1]) # Split pour creer une list avec tous les mots de DescriptionCours

    for i in range(0,len(words)):
        words[i] = stemmer.stem(words[i]) #Réduction des mots à leur racine
    dict_words = OrderedCounter(words)
    bigListD.append(dict_words)

    for i in range(0,len(words)): # On crée un liste avec tous les mots, on enlèvera les doublons après
        bigListW.append(words[i])


# Fonction main

if __name__ == '__main__':


    #path = '/home/corentin/Maitrise/Cours/INF8007/TD2/Testizi'
    path = '/home/corentin/Maitrise/Cours/INF8007/TD2/PolyHEC'

    stemmer = SnowballStemmer('french')
    words = []
    bigListW = []
    bigListD = [] # Une liste de tous les dictionnaires associés à chaque description de cours
    dictIndex = {}
    courseDesc = []
    Mdata = []
    Mrow = []
    Mcol = []
    d = 0
    n = 0

    class OrderedCounter(Counter, OrderedDict):
        pass

    for filename in tqdm(glob.glob(os.path.join(path, '*.txt'))):
            with open(filename) as f: # No need to specify 'r': this is the default.
                content = f.read()
                wordSep(content)
                f.close()
                d += 1

    print('\n')
    bigListW =  list(set(bigListW))
    #print(bigListW)
    n = len(bigListW)

    for x in bigListW:
        dictIndex[x] = bigListW.index(x)


    #print(bigListW)
    #print(dictIndex)
    prepMatrix(n,d)
    matrix = csr_matrix((Mdata, (Mrow, Mcol)), shape=(n, d))
    print(matrix.A)
