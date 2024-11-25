from rest_framework import serializers
from .models import Client, Compte

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ['id', 'nom', 'prenom', 'email', 'etat']


class CompteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Compte
        fields = ['id', 'client', 'type_compte', 'solde']
