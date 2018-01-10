from .models import Cluster, Clusterizacao , Review
from rest_framework import serializers
from Clusterizacao.Ensemble import Ensemble
import json

class ReviewSerializer(serializers.ModelSerializer):

    class Meta:
        model = Review
        fields = ('__all__')


class ClusterSerializer(serializers.ModelSerializer):
    reviews = ReviewSerializer(many=True, read_only=True)

    class Meta:
        model = Cluster
        fields=('__all__')

class ClusterizacaoSerializer(serializers.ModelSerializer):
    clusters = ClusterSerializer(many=True, read_only=True)

    class Meta:
        model = Clusterizacao
        fields = ('__all__')

    def create(self,data):
        frases = json.loads(data['ecommerce'])
        reviews = []
        for opnion in frases['opinions']:
            reviews.append((opnion['text'],opnion['data']))

        ensemble = Ensemble()
        clusterizacao = Clusterizacao()

        clusterizacao.ecommerce = frases['ecommerce']
        temas,clusters = ensemble.clusterizar(reviews)
        clusterizacao.save()
        ind = 0

        for tema in temas:
            cluster = Cluster()
            cluster.title = tema
            cluster.clusterizacao = clusterizacao
            cluster.save()
            for frase in clusters[ind]:
                review = Review()
                review.text = frase[2]
                review.cluster = cluster
                review.data = frase[1]
                review.save()
            ind = ind+1

        return clusterizacao