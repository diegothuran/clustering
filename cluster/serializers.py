from .models import Cluster, Clusterizacao , Review
from rest_framework import serializers
from Clusterizacao.Ensemble import Ensemble

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

    def create(self,request, *args, **kwargs):
        ensemble = Ensemble()
        clusterizacao = Clusterizacao()
        clusterizacao.ecommerce = "Centauro"
        temas,clusters = ensemble.clusterizar()
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