from rest_framework import generics, status
from rest_framework.response import Response
from .models import Client, Compte
from .serializers import *
from rest_framework.views import APIView
from rest_framework import status
from django.shortcuts import get_object_or_404

class ClientCreateView(generics.ListCreateAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer

class ClientDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    lookup_field = 'id'

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        # Filtrer les données de la requête pour exclure les champs sensibles
        data = request.data.copy()
        excluded_fields = ['password', 'pass_send', 'user', 'created_by']
        update_data = {key: value for key, value in data.items() if key not in excluded_fields}

        # Convertir les valeurs booléennes si nécessaire
        bool_fields = ['isActive']
        for field in bool_fields:
            if field in update_data:
                update_data[field] = update_data[field].lower() == 'true'

        # Mettre à jour les champs directement sur l'instance
        for key, value in update_data.items():
            setattr(instance, key, value)

        instance.save()

        # Sérialiser et renvoyer les données mises à jour
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

class CompteCreateView(generics.CreateAPIView):
    queryset = Compte.objects.all()
    serializer_class = CompteSerializer

    def create(self, request, *args, **kwargs):
        # Vérification de l'existence du `client_id` dans les données
        client_id = request.data.get('client_id')
        if not client_id:
            return Response(
                {"error": "Le champ 'client_id' est requis."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Vérifier si le client existe
        client = get_object_or_404(Client, id=client_id)

        # Préparer les données pour le serializer
        data = request.data.copy()
        data['client'] = client.id  # Inclure le client dans les données

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer, client)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer, client):
        # Passer explicitement l'objet `client` au serializer
        serializer.save(client=client)


class ClientComptesListView(generics.ListAPIView):
    """
    Vue pour récupérer tous les codes de comptes d'un client donné.
    """
    serializer_class = CompteCodeSerializer

    def get_queryset(self):
        client_id = self.kwargs['client_id']
        return Compte.objects.filter(client_id=client_id).only('code')
    

class CompteDetailView(generics.RetrieveAPIView):
    """
    Vue pour afficher les détails d'un compte en fonction du code.
    """
    queryset = Compte.objects.all()
    serializer_class = CompteDetailSerializer
    lookup_field = 'code'  # Recherche le compte via le champ 'code'


class ClientActivationView(generics.UpdateAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientActivationSerializer
    lookup_field = 'id'  # Utilise l'ID pour identifier un client

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Le statut du compte a été mis à jour avec succès"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class ValidateClientView(APIView):
    def patch(self, request, pk):
        try:
            client = Client.objects.get(pk=pk)
            if client.etat == 'temporaire':
                client.etat = 'final'
                client.save()
                return Response({"message": "Client validé avec succès."}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "Le client est déjà validé."}, status=status.HTTP_400_BAD_REQUEST)
        except Client.DoesNotExist:
            return Response({"message": "Client introuvable."}, status=status.HTTP_404_NOT_FOUND)
        

class CancelClientView(APIView):
    def delete(self, request, pk):
        try:
            client = Client.objects.get(pk=pk, etat='temporaire')
            client.delete()
            return Response({"message": "Client et ses comptes supprimés avec succès."}, status=status.HTTP_200_OK)
        except Client.DoesNotExist:
            return Response({"message": "Client introuvable ou déjà validé."}, status=status.HTTP_404_NOT_FOUND)
