#!/usr/bin/python3

import re
import sys
import os
import glob
import numpy as np
from collections import Counter


def fillMatrix(n,d):
    for j in range(0,d):
        for i in range(0,n):
            for key in bigListD[j]:
                matrix[bigListW.index(key),j]=bigListD[j][key]
                #print(bigListW.index(key))

def word_sep(content):
    dict_words = {}
    regex_word = r'\W+'
    regex_space = r'\s'

    CleanString = re.sub('\W+',' ',content) # Ajoute d'un espace avant les points

    #Remplacer par racine et enlever mots inutiles

    words = re.split(regex_word,CleanString) # Split pour creer une list avec tous les mots
    dict_words = Counter(words)
    bigListD.append(dict_words)

    for i in range(0,len(words)): # On crée un liste avec tous les mots, on enlèvera les doublons après
        bigListW.append(words[i])

# Fonction main

if __name__ == '__main__':

    path = '/home/corentin/Maitrise/Cours/INF8007/TD2/Test'
    #path = '/home/corentin/Maitrise/Cours/INF8007/TD2/PolyHEC'

    words = []
    bigListW = []
    bigListD = [] # Une liste de tous les dictionnaires associés à chaque description de cours
    d = 0
    n = 0

    for filename in glob.glob(os.path.join(path, '*.txt')):
            with open(filename) as f: # No need to specify 'r': this is the default.
                content = f.read()
                word_sep(content)
                f.close()
                d += 1

    #print(bigListW)
    print('\n\n\n')
    bigListW =  list(set(bigListW))
    #print(bigListW)
    n = len(bigListW)
    matrix = np.zeros((n,d), dtype=np.int)
    fillMatrix(n,d)
    print(matrix)
