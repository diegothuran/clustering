# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from rest_framework import generics
from .models import Cluster
from .serializers import ClusterSerializer

class ClusterList(generics.ListCreateAPIView):
    queryset = Cluster.objects.all()
    serializer_class = ClusterSerializer