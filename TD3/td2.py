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

def recom(classCode,nbreq):
	path = 'PolyHEC/'

	#---------------- Definitions des variables ----------------------#
	words = []
	listWReq =[]
	dictIdf = {}
	dictIndex = {} # Dictionnaire des cours et des indexs associés
	courseDesc = []
	bigListD = []
	bigListW = []
	d = 0
	n = 0

	reqDict = {}

	class OrderedCounter(Counter, OrderedDict): # Pour que le Counter garde l'ordre de lecture
		pass

	#------------------- Gestion des pickles --------------------#
	try:
		with open( "filesContent.p", "rb") as f:
			reqDict = pickle.load( f )
			V = pickle.load(f)

	except (OSError, IOError) as e:

		for filename in tqdm(glob.glob(os.path.join(path, '*.txt'))):
			with open(filename) as f:
				temp = filename.replace('PolyHEC/','')
				reqDict[temp.replace('.txt','')] = d # Creation d'un dict des fichiers et de leur indices
				content = f.read()
				bigListD,bigListW =  wordSep(content,bigListD,bigListW) #Séparation des mots dans les fichiers
				f.close()
				d += 1 #Compte du nombre de fichiers
		dictIdf = OrderedCounter(bigListW)
		bigListW =  list(set(bigListW)) # Pour enlever les doublons
		n = len(bigListW)
		for x in bigListW:
			dictIndex[x] = bigListW.index(x) # Liste des index pour la matrice creuse

		Mdata,Mrow,Mcol = prepMatrix(n,d,bigListD,dictIndex) # Préparation des paramètres de la matrice

		matF = csr_matrix((Mdata, (Mrow, Mcol)), shape=(n, d)) # Création matrice creuse
		matTFIFD = matF
		matTFIFD = tfidf(matTFIFD,d)
		uMatrix,vlp,V = svds(matTFIFD, k = 32) # Réduction SVD
		V = vlp.reshape(-1,1)*V

		with open("filesContent.p", "wb") as f:
			pickle.dump( reqDict, f )
			pickle.dump( V, f ) #Sauvegarde de la matrice TFIDF dans le pickle

	#---------------- Traitement normal avec ou sans pickle----------------------#

	req = reqDict[classCode.upper()] # Récupération de la requête

	distance = [] #Liste des distances
	distanceSmall = [] #Liste des distances les plus hautes
	cosine(req,V,distance)
	recommendationsData = []

	coursesIndexes = np.argsort(distance)[-int(nbreq):][::-1] # Tri des distances

	for i in range(0, len(coursesIndexes)):
		distanceSmall.append(distance[coursesIndexes[i]])
	courseNames = []

	for i in range(0,len(coursesIndexes)):
		for name , index in reqDict.items():
			if index == (coursesIndexes[i]):
				courseNames.append(name) # Récupération des noms de cours dans le dictionnaire

	for i in range(0,len(courseNames)):
		recommendationsData.append(request(courseNames[i]))
		recommendationsData[i]['similarity']=distanceSmall[i]

	print('Finished')
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

def cosine(req,V,distance):
	for i in range (V.shape[1]):

		if (np.linalg.norm(V[:,req])*np.linalg.norm(V[:,i])) == 0 :
			distance.append(0)
		else:
			distance.append(float(np.dot(V[:,req], V[:,i].T) / (np.linalg.norm(V[:,req]) * np.linalg.norm(V[:,i]))))

	return distance


#-----------------------------------------------------------------------------------------------------tfidf calcul
def tfidf(matTFIFD,d):
	df = ((matTFIFD>0).sum(axis=1)).reshape(-1)
	idf = np.log(d/df)
	idf = np.diagflat(idf)
	matTFIFD = matTFIFD.T.dot(idf).T # Meilleure solution sans np.take. On repasse tout en sparse matrix pour accélérer la suite, pas grave avec le pickle
	matTFIFD = csc_matrix(matTFIFD)
	return matTFIFD

#------------------------------------------------------------------------------------------- sparse matrice preparation

def prepMatrix(n,d,bigListD,dictIndex):
	Mdata = []
	Mrow = []
	Mcol = []
	for j in range(0,d):
		for key in bigListD[j]:
			Mdata.append(bigListD[j][key])
			Mrow.append(dictIndex[key])
		for i in range(0,len(bigListD[j])):
			Mcol.append(j)
	return Mdata,Mrow,Mcol

#----------------------------------------------------------------------------------------------------------------- parser

def wordSep(content,bigListD,bigListW):

	class OrderedCounter(Counter, OrderedDict): # Pour que le Counter garde l'ordre de lecture
		pass

	dict_words = {}
	regex_word = r'\W+'
	regex_space = r'\s'
	regex_des = 'DescriptionCours'

	CleanString = re.sub('\W+',' ',content) # Ajoute d'un espace avant les points

	#Remplacer par racine et enlever mots inutiles
	courseDesc = re.split(regex_des,CleanString)
	words = re.split(regex_word,courseDesc[1]) # Split pour creer une list avec tous les mots de DescriptionCours

	for i in range(0,len(words)):
		words[i] = SnowballStemmer('french').stem(words[i]) #Réduction des mots à leur racine
	dict_words = OrderedCounter(words)
	bigListD.append(dict_words)

	for i in range(0,len(words)): # On crée un liste avec tous les mots, on enlèvera les doublons après
		bigListW.append(words[i])

	return bigListD,bigListW

#------------------------------------------------------------------------------------------------------------------main

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument("file")
	parser.add_argument("--nbreq", type=int, default=5)
	parser.add_argument("--svd", type=int, default=32) # Ne marche que lorsqu'il n'y a pas de pickle , améliorable
	args = parser.parse_args() # Récipération des argiments pour modifier nombre de comparaisons
