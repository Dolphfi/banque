from rest_framework import generics, status
from rest_framework.response import Response
from .models import Client, Compte
from .serializers import ClientSerializer, CompteSerializer
from rest_framework.views import APIView
from rest_framework import status

class ClientCreateView(generics.CreateAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer


class CompteCreateView(generics.CreateAPIView):
    queryset = Compte.objects.all()
    serializer_class = CompteSerializer

    def create(self, request, *args, **kwargs):
        client_id = request.data.get('client')
        try:
            client = Client.objects.get(id=client_id, etat='temporaire')
        except Client.DoesNotExist:
            return Response({"error": "Client introuvable ou non temporaire"}, status=status.HTTP_400_BAD_REQUEST)

        return super().create(request, *args, **kwargs)



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
