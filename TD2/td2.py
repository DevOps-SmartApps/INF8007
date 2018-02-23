#!/usr/bin/python3

import re
import sys
import os
import glob
import numpy as np
from collections import *
from nltk.stem.snowball import SnowballStemmer
from scipy.sparse import csr_matrix
from scipy.sparse import csc_matrix
from scipy.sparse.linalg import svds, eigs
from scipy import linalg
from numpy.linalg import inv
from tqdm import tqdm
import pickle

#----------------------------------------------------------------------------------------------------- cosinus




#-----------------------------------------------------------------------------------------------------tfidf calculator

def tfidf(matTFIFD,d):
    #matTFIFD = matTFIFD.toarray() # pas possible trop de mémoire
    df = ((matTFIFD>0).sum(axis=1)).reshape(-1)
    idf = np.log(d/df)
    idf = np.diagflat(idf)
    #print(idf)
    #matTFIFD = matTFIFD*idf
    #matTFIFD = matTFIFD.T
    matTFIFD = matTFIFD.T.dot(idf).T # Faux à priori, vérifier la kouill'




#------------------------------------------------------------------------------------------- sparse matrice preparation

def prepMatrix(n,d):
    for j in range(0,d):
        for key in bigListD[j]:
            Mdata.append(bigListD[j][key])
            Mrow.append(dictIndex[key])
            #Mrow.append(bigListW.index(key))
        for i in range(0,len(bigListD[j])):
            Mcol.append(j)

#-----------------------------------------------------------------------------------------------------------------parser

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

#------------------------------------------------------------------------------------------------------------------main

if __name__ == '__main__':

    #path = '/home/corentin/Maitrise/Cours/INF8007/TD2/Testizi'
    path = '/home/corentin/Maitrise/Cours/INF8007/TD2/PolyHEC'

#---------------- Definitions des variables ----------------------#
    stemmer = SnowballStemmer('french')
    words = []
    listWReq =[]

    bigListW = []
    bigListD = [] # Une liste de tous les dictionnaires associés à chaque description de cours
    dictIdf = {}
    dictIndex = {}
    courseDesc = []
    Mdata = []
    Mrow = []
    Mcol = []
    d = 0
    n = 0

    reqDict = {}

    class OrderedCounter(Counter, OrderedDict): # Pour que le Counter garde l'ordre de lecture
        pass

#------------------- Traitement de données --------------------#
    try:
        with open( "filesContent.p", "rb") as f:
            bigListD = pickle.load( f )
            bigListW = pickle.load( f )
            d = pickle.load( f )
            reqDict = pickle.load( f )

    except (OSError, IOError) as e:

        for filename in tqdm(glob.glob(os.path.join(path, '*.txt'))):
            with open(filename) as f: # No need to specify 'r': this is the default.
                temp = filename.replace('%s/' % path,'')
                reqDict[temp.replace('.txt','')] = d # Creation d'un dict des fichiers et de leur indices
                content = f.read()
                wordSep(content)
                f.close()
                d += 1
        with open( "filesContent.p", "wb") as f:
            pickle.dump( bigListD, f )
            pickle.dump( bigListW, f )
            pickle.dump( d, f ) # Créer une fonction pour ça, mais besoin  d'appeler wordSep dedans
            pickle.dump( reqDict, f )

    dictIdf = OrderedCounter(bigListW)
    bigListW =  list(set(bigListW)) # Pour enlever les doublons
    n = len(bigListW)
    for x in bigListW:
        dictIndex[x] = bigListW.index(x) # Liste des index pour la matrice creuse

    prepMatrix(n,d) # Creation de la matrice

    matF = csr_matrix((Mdata, (Mrow, Mcol)), shape=(n, d))
    matF = matF.asfptype() # Cast en float pour le svd
    req = matF[:,reqDict[sys.argv[1]]] # Récupération de la requête
    matTFIFD = matF # a corriger ici
    tfidf(matTFIFD,d)
    print('tfidf ok\n')
    #print(matF)
    #Calcul du cos
    uMatrix,vlp,Vt = svds(matTFIFD, k = 2) # Réduction SVD ,

    uMatrix = uMatrix*vlp# uMatrix a pour dimensions n*k on multiplie par les vlp.
    #print(req.T.shape)
    req = req.T.dot(uMatrix)
    print(req.shape)

    print('\n\n')

    # Faire la requête, transformer bigListW en dictionnaire avec le nombre d'occurences du mot pour récupérer ses values dans le tfidf.
