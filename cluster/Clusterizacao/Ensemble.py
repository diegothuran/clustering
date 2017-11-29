# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import sys
from summa import summarizer
import csv
from spellchecker import Spellchecker
from DBSCAN import Dbscan
from PreProcessamento import PreProcesso
from ExtracaoSujeito import ExtracaoSujeito
reload(sys)
sys.setdefaultencoding('utf-8')

class Ensemble():
    def __init__(self):
        self.preProc = PreProcesso()
        self.dbscan = Dbscan()
        self.extrator = ExtracaoSujeito()
        self.not_temas = ['d', '.', 'ok', '10', 'on', 'NO SUGGESTION', 'gr', 'procos']
        self.spell = Spellchecker()

    def buscar(self):
        reviews =[]
        dataPath = 'cluster/Clusterizacao/teste11.csv'
        p = PreProcesso()
        with open(dataPath, 'rb') as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) == 2:
                    if row[1] != "":
                        frase = p.prePorcessar(row[0])
                        reviews.append((frase, row[1], row[0]))
        print('=========== DONE =============================')
        return reviews

    def clusterizar(self):
        reviews = self.buscar()
        clusters = self.dbscan.dbScan(reviews, 0.3, 5)

        topicos = []
        for cluster in clusters:
            comentario = ''
            for frase in cluster:
                comentario = comentario + frase[2] + " "

            topicos.append(comentario)

        # Juntando Cluster que possuem mesmo tema

        temas = []
        clusters = []
        for frase in topicos:
            try:
                tema = self.spell.correct(
                    self.extrator.extrair(summarizer.summarize(frase, words=20, language='portuguese')))
                if tema not in temas:
                    temas.append(tema)
                    clusters.append(frase)
                else:
                    ind = temas.index(tema)
                    cluster = clusters[ind]
                    clusters[ind] = cluster + " " + frase
            except:
                print("Sem Tema")

        # IDENTIFICAÇÂO DE TEMA FINAL

        temas = [self.spell.correct(self.extrator.extrair(summarizer.summarize(frase, words=20, language='portuguese'))) for
             frase in clusters]
        temas = list(set(temas))
        temas_final = []
        for tema in temas:
            if tema not in self.not_temas:
                temas_final.append(tema)
        #return temas_final[0]
        return "Loja"