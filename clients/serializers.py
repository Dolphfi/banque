from rest_framework import serializers
from .models import Client, Compte

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = "__all__"
        extra_kwargs = {
            'password': {'read_only': True},
            'pass_send': {'read_only': True},
            'username': {'read_only': True},
        }


class CompteCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Compte
        fields = ['code']  # Retourne uniquement le champ code

class CompteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Compte
        fields = '__all__'
        extra_kwargs = {
            'code': {'read_only': True},
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True},
        }

    def validate(self, attrs):
        # Validation supplémentaire si nécessaire
        if attrs['type_compte'] == 'SOL' and (attrs['sol'] <= 0 or attrs['nb_main'] <= 0):
            raise serializers.ValidationError("Solde et nombre de mains doivent être positifs pour le type SOL.")
        return attrs
    


class CompteDetailSerializer(serializers.ModelSerializer):
    nom = serializers.SerializerMethodField()
    prenom = serializers.SerializerMethodField()

    class Meta:
        model = Compte
        fields = '__all__'  # Inclut tous les champs de Compte, ainsi que `nom` et `prenom`

    def get_nom(self, obj):
        return obj.client.nom  # Récupère le nom depuis le modèle Client

    def get_prenom(self, obj):
        return obj.client.prenom  # Récupère le prénom depuis le modèle Client

class ClientActivationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ['isActive']  # Inclut uniquement le champ isActive
