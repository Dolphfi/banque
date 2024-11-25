import uuid
from django.db import models

class Client(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nom = models.CharField(max_length=255)
    prenom = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    etat = models.CharField(
        max_length=10,
        choices=[('temporaire', 'Temporaire'), ('final', 'Final')],
        default='temporaire'
    )

    def __str__(self):
        return f"{self.nom} {self.prenom} ({self.etat})"


class Compte(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='comptes')
    type_compte = models.CharField(max_length=255)
    solde = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Compte {self.type_compte} - Solde: {self.solde}€"
