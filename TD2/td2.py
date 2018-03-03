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
from scipy.sparse.linalg import inv
from tqdm import tqdm
import pickle


#----------------------------------------------------------------------------------------------------- print fin
def nomCours(classCode):
	titlePattern = re.compile("TitreCours")
	title = ""
	with open("PolyHEC/" + classCode + ".txt", "r") as classFile:
		for line in classFile:
			if re.match(titlePattern, line) :
				title = line.split(": ")[1]
				title = re.sub("\n", "", title)
	return title

# Returns the description of a course
def descriCours(classCode):
	descPattern = re.compile("DescriptionCours")
	description = ""
	with open("PolyHEC/" + classCode + ".txt", "r") as classFile:
		for line in classFile:
			if re.match(descPattern, line) :
				description = line.split(": ")[1]
				description = re.sub("\n", "", description)
	return description


#----------------------------------------------------------------------------------------------------- cosinus

def cosine(req,V): # A corriger
    for i in range (V.shape[1]):

        if (np.linalg.norm(V[:,req])*np.linalg.norm(V[:,i])) == 0 :
            distance.append(0)
        else:
            distance.append(float(np.dot(V[:,req], V[:,i].T) / (np.linalg.norm(V[:,req]) * np.linalg.norm(V[:,i]))))


#-----------------------------------------------------------------------------------------------------tfidf calculator
#def tfidf(matTFIFD,d):
#    df = ((matTFIFD>0).sum(axis=1))
#    idf = np.log(d/df)
#    print(idf.shape)
#    print(matTFIFD.shape)
#    matTFIFD = idf*matTFIFD
    #print(matTFIFD)

# -- Version diagonalisation
def tfidf(matTFIFD,d):
    print("Preparation matTFIFD \n")
    df = ((matTFIFD>0).sum(axis=1)).reshape(-1)
    idf = np.log(d/df)
    idf = np.diagflat(idf)
    matTFIFD = matTFIFD.T.dot(idf).T # Faux à priori, vérifier la kouill'
    matTFIFD = csc_matrix(matTFIFD)
    #print(matTFIFD)
    print("matTFIFD OK \n") # Add a pickle here
    return matTFIFD

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

    #path = '/home/corentin/Maitrise/Cours/INF8007/TD2/Test'
    path = 'PolyHEC/'

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
            V = pickle.load(f)

    except (OSError, IOError) as e:

        #for filename in tqdm(glob.glob(os.path.join(path, '*.txt'))):
        for filename in tqdm(glob.glob(os.path.join(path, '*.txt'))):
            with open(filename) as f:
                temp = filename.replace('PolyHEC/','')
                reqDict[temp.replace('.txt','')] = d # Creation d'un dict des fichiers et de leur indices
                content = f.read()
                wordSep(content)
                f.close()
                d += 1
        dictIdf = OrderedCounter(bigListW)
        bigListW =  list(set(bigListW)) # Pour enlever les doublons
        n = len(bigListW)
        for x in bigListW:
            dictIndex[x] = bigListW.index(x) # Liste des index pour la matrice creuse

        prepMatrix(n,d) # Creation de la matrice

        matF = csr_matrix((Mdata, (Mrow, Mcol)), shape=(n, d))
        #matF = matF.asfptype() # Cast en float pour le svd
        matTFIFD = matF # a corriger ici
        matTFIFD = tfidf(matTFIFD,d)
        uMatrix,vlp,V = svds(matTFIFD, k = 32) # Réduction SVD
        V = vlp.reshape(-1,1)*V

        with open("filesContent.p", "wb") as f:
            pickle.dump( bigListD, f )
            pickle.dump( bigListW, f )
            pickle.dump( d, f )
            pickle.dump( reqDict, f )
            pickle.dump( V, f )

    req = reqDict[sys.argv[1].upper()] # Récupération de la requête

    # uMatrix a pour dimensions n*k on multiplie par les vlp.
    distance = []
    cosine(req,V)

    coursesIndexes = np.argsort(distance)[-6:][::-1]
    courseNames = []

    for i in range(0,len(coursesIndexes)):
        for name , index in reqDict.items():
            if index == (coursesIndexes[i]):
                courseNames.append(name)

    output = sys.argv[1].upper()
    output = output.split(".")[0] + "_Comp.txt"
    out_F = open(output,"w")
    out_F.write("Compared class : " + sys.argv[1].lower() + "\n")
    out_F.write("Titre : " + nomCours(sys.argv[1].upper()) + "\n")
    out_F.write("Description: " + descriCours(sys.argv[1].upper()) + "\n")
    out_F.write("\n")

    for i in range(0,len(coursesIndexes)):
        out_F.write(courseNames[i].lower() + " : " + str(distance[coursesIndexes[i]]) + "\n")
        out_F.write("Titre : " + nomCours(courseNames[i]) + "\n")
        out_F.write("Description : " + descriCours(courseNames[i]) + "\n")
        out_F.write("\n")

    out_F.close()
