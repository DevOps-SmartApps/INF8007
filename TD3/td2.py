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
import argparse

def request(classCode):
# Liste
	request_dict = {'id': classCode, 'title': nomCours(classCode.upper()), 'description': descriCours(classCode.upper())}
	return request_dict

def recom(classCode):
	path = 'PolyHEC/'

	#---------------- Definitions des variables ----------------------#
	stemmer = SnowballStemmer('french')
	words = []
	listWReq =[]

	bigListW = [] # Une liste de tous les mots qui seront rencontrés dans les fichiers
	bigListD = [] # Une liste de tous les dictionnaires associés à chaque description de cours
	dictIdf = {}
	dictIndex = {} # Dictionnaire des cours et des indexs associés
	courseDesc = []
	Mdata = []
	Mrow = []
	Mcol = []
	d = 0
	n = 0

	reqDict = {}

	class OrderedCounter(Counter, OrderedDict): # Pour que le Counter garde l'ordre de lecture
		pass


	#------------------- Gestion des pickles --------------------#
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
				wordSep(content) #Séparation des mots dans les fichiers
				f.close()
				d += 1 #Compte du nombre de fichiers
		dictIdf = OrderedCounter(bigListW)
		bigListW =  list(set(bigListW)) # Pour enlever les doublons
		n = len(bigListW)
		for x in bigListW:
			dictIndex[x] = bigListW.index(x) # Liste des index pour la matrice creuse

		prepMatrix(n,d) # Préparation des paramètres de la matrice

		matF = csr_matrix((Mdata, (Mrow, Mcol)), shape=(n, d)) # Création matrice creuse
		matTFIFD = matF
		matTFIFD = tfidf(matTFIFD,d)
		uMatrix,vlp,V = svds(matTFIFD, k = args.svd) # Réduction SVD
		V = vlp.reshape(-1,1)*V

		with open("filesContent.p", "wb") as f:
			pickle.dump( bigListD, f )
			pickle.dump( bigListW, f )
			pickle.dump( d, f )
			pickle.dump( reqDict, f )
			pickle.dump( V, f ) #Sauvegarde de la matrice TFIDF dans le pickle



	parser = argparse.ArgumentParser()
	parser.add_argument("file")
	parser.add_argument("--nbreq", type=int, default=5)
	parser.add_argument("--svd", type=int, default=32) # Ne marche que lorsqu'il n'y a pas de pickle , améliorable
	args = parser.parse_args() # Récipération des argiments pour modifier nombre de comparaisons



	#---------------- Traitement normal avec ou sans pickle----------------------#

	req = reqDict[args.file.upper()] # Récupération de la requête

	distance = [] #Liste des distances
	cosine(req,V)
	recommendationsData = []

	coursesIndexes = np.argsort(distance)[-args.nbreq:][::-1] # Tri des distances
	courseNames = []

	for i in range(0,len(coursesIndexes)):
		for name , index in reqDict.items():
			if index == (coursesIndexes[i]):
				courseNames.append(name) # Récupération des noms de cours dans le dictionnaire

	for i in range(0,len(courseNames)):
		recomList.append(nomCours(courseNames[i]))
		recomList[i]['similarity']=distance[i]

	print(recommendationsData)
	return recommendationsData



#-----------------------------------------------------------------------------------------------------  Récupération des contenus
def nomCours(classCode):
	titre = ""
	regexTitre = re.compile("TitreCours")
	with open("PolyHEC/" + classCode + ".txt", "r") as F:
		for line in F:
			if re.match(regexTitre, line) :
				titre = line.split(": ")[1]
				titre = re.sub("\n", "", titre)
	return titre


def descriCours(classCode):
	description = ""
	regexDesc = re.compile("DescriptionCours")
	with open("PolyHEC/" + classCode + ".txt", "r") as F:
		for line in F:
			if re.match(regexDesc, line) :
				description = line.split(": ")[1]
				description = re.sub("\n", "", description)
	return description


#----------------------------------------------------------------------------------------------------- cosinus

def cosine(req,V):
    for i in range (V.shape[1]):

        if (np.linalg.norm(V[:,req])*np.linalg.norm(V[:,i])) == 0 :
            distance.append(0)
        else:
            distance.append(float(np.dot(V[:,req], V[:,i].T) / (np.linalg.norm(V[:,req]) * np.linalg.norm(V[:,i]))))


#-----------------------------------------------------------------------------------------------------tfidf calcul
def tfidf(matTFIFD,d):
    df = ((matTFIFD>0).sum(axis=1)).reshape(-1)
    idf = np.log(d/df)
    idf = np.diagflat(idf)
    matTFIFD = matTFIFD.T.dot(idf).T # Meilleure solution sans np.take. On repasse tout en sparse matrix pour accélérer la suite, pas grave avec le pickle
    matTFIFD = csc_matrix(matTFIFD)
    return matTFIFD

#------------------------------------------------------------------------------------------- sparse matrice preparation

def prepMatrix(n,d):
    for j in range(0,d):
        for key in bigListD[j]:
            Mdata.append(bigListD[j][key])
            Mrow.append(dictIndex[key])
        for i in range(0,len(bigListD[j])):
            Mcol.append(j)

#----------------------------------------------------------------------------------------------------------------- parser

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



    output = args.file.upper()
    output = output.split(".")[0] + "_Comp.txt"
    out_F = open(output,"w")
    out_F.write("Compared class : " + args.file.lower() + "\n")
    out_F.write("Titre : " + nomCours(args.file.upper()) + "\n")
    out_F.write("Description: " + descriCours(args.file.upper()) + "\n")
    out_F.write("\n")

    for i in range(0,len(coursesIndexes)):
        out_F.write(courseNames[i].lower() + " : " + str(distance[coursesIndexes[i]]) + "\n")
        out_F.write("Titre : " + nomCours(courseNames[i]) + "\n")
        out_F.write("Description : " + descriCours(courseNames[i]) + "\n")
        out_F.write("\n")

    out_F.close()
