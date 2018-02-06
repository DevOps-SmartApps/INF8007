#!/usr/bin/python3

#Code du TD1 du cours INF8007

import pyphen
import re
import sys
import os


dic = pyphen.Pyphen(lang='en') # On met la langue en anglais pour pyphen

#Définition des fonctions :


#Fonction pour écrire le fichier voulu. Plusieurs write pour gérer les retours à la ligne

def my_print(bool_write,i,hyp_clean,nb_hyp,words,nb_words,sentences,nb_sentences,Flesch_i):
    if bool_write:
        fr.write('Line %s\n%s\n' % (i,'-'*(5+len(str(i)))))
        fr.write('Syllables:\n%s\nTotal: %d\n\nWords:\n%s\nTotal: %d\n\nSentences:\n%s\nTotal: %d\n\nTotal: %.3f\n' % ('-'.join(hyp_clean),nb_hyp,"-".join(words),nb_words,'-'.join(sentences),nb_sentences,Flesch_i))

    else:
        fr.write('\n\nLine %s\n%s\n' % (i,'-'*(5+len(str(i)))))
        fr.write('Syllables:\n%s\nTotal: %d\n\nWords:\n%s\nTotal: %d\n\nSentences:\n%s\nTotal: %d\n\nTotal: %.3f\n' % ('-'.join(hyp_clean),nb_hyp,"-".join(words),nb_words,'-'.join(sentences),nb_sentences,Flesch_i))

#Fonction qu'on réutilisera probablement dans le TD2 pour découper les lignes

def traitement(bool_write,line,i):
    regex_word = r'\s'
    regex_sentence =  r'([.]{3}|[.?!])'
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

    inputfile = sys.argv[1]
    out_f = inputfile.split(".")[0] + "__solution.txt" #on a récupéré le nom de l'input et on lui ajoute une extension de la forme demandée

    fr  = open(out_f, 'w')
    i = 0; #Pour compter les lignes

    with open(sys.argv[1], "r") as f:
        bool_write = True

        for line in f:
            i += 1
            traitement(bool_write,line,i)
            bool_write = False


    fr.close()
