#!/usr/bin/python3

import re
import sys
import os
import glob
import pandas as pd
import numpy as np


def traitement(bool_write,line,i):
    regex_word = r'\s'

    regex_hyp = r'\-|\s'
    hyp = []
    hyp_clean = []
    line = line.replace('\n','')
    line_space = re.sub(regex_sentence,r' \1',line) # Ajoute d'un espace avant les points
    line_space = re.sub(',',r' ,',line_space)
    line_space = re.sub(';',r' ;',line_space)
    line_space = re.sub('\'',' \'',line_space)
    line_space = re.sub(':',r' :',line_space)

    #je les gère au cas par cas pour avoir un fichier en sortie identique à celui demandé mais pas très robuste comme façon de faire

    words = re.split(regex_word,line_space) # Split pour creer une list avec tous les mots
    sentences = re.split(regex_sentence,line)
    del sentences[len(sentences)-1]
    sentences =  [x + y for x, y in zip(sentences[::2], sentences[1::2])]
    sentences = [x.strip(' ') for x in sentences]

    for x in words:
        hyp.append(re.split(regex_hyp,dic.inserted(x)))

    for x in hyp:
        if len(x)>1:
            for y in x:
                hyp_clean.append(y)
        else:
            hyp_clean.append(x[0]) # Pour eviter le []

    nb_hyp = len(hyp_clean)
    nb_words = len(words)
    nb_sentences = len(sentences)-(sentences.count('.')+sentences.count('...')+sentences.count('?')+sentences.count('!'))
    # On aurait pu laisser juste '.' et '...' dans le cas de train mais cela permet une meilleure ré-utilisabilité du script de mettre tous les cas de fin de phrase.

    Flesch_i = 206.835-1.015*(nb_words/nb_sentences)-84.6*(nb_hyp/nb_words)
    my_print(bool_write,i,hyp_clean,nb_hyp,words,nb_words,sentences,nb_sentences,Flesch_i)

# Fonction main

if __name__ == '__main__':

    path = '/home/corentin/Maitrise/Cours/INF8007/TD2/TEST'
    #path = '/home/corentin/Maitrise/Cours/INF8007/TD2/PolyHEC'

    file_in = list()

    for filename in glob.glob(os.path.join(path, '*.txt')):
            with open(filename) as f: # No need to specify 'r': this is the default.
                content = f.read()
                df_prim = pd.DataFrame(content, columns = ['raw'])
                df_prim['titre'] = df_prim['raw'].str.extract('TitreCours', expand=True)
                df_prim['description'] = df_prim['raw'].str.extract(r'\:\-([^\-]*)', expand=True)

                print(filename, len(content))

        #file_trgt = sys.argv[1]

        #out_f = inputfile.split(".")[0] + "__solution.txt" #on a récupéré le nom de l'input et on lui ajoute une extension de la forme demandée

        #fr  = open(out_f, 'w')
    print(content)
    i = 0; #Pour compter les lignes
