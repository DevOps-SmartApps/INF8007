import pytest
from td2.py import nomCours
from td2.py import cosine


def test_cosine():
    req = [-0.2140,-0.1821]
    D1 = [-0.6458,-0.7194]
    assert cosine(req,D1) == 0.9910
    assert cosine(req,req) == 1.0


def test_nomCours():
    assert nomCours(inf8007) == 'Langages de script'
    assert nomCours(STT2700) == 'Concepts et methodes en statistique'
