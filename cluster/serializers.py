from .models import Cluster
from rest_framework import serializers
from Clusterizacao.Ensemble import Ensemble
class ClusterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cluster
        fields = ('__all__')

    def create(self,request, *args, **kwargs):
        ensemble = Ensemble()
        clusters = []
        cluster = Cluster()
        cluster.title = ensemble.clusterizar()
        clusters.append(cluster)

        cluster = Cluster()
        cluster.title = "Produto"
        cluster.save()
        clusters.append(cluster)
        return clusters