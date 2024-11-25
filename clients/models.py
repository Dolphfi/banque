import uuid
from django.db import models
from django.contrib.auth.hashers import check_password as django_check_password,make_password
from django.utils.crypto import get_random_string
import string
import random
from api.models import User
from banque import settings
import pytz
from django.utils import timezone

def get_local_timezone():
    return pytz.timezone(getattr(settings, 'DEFAULT_TIMEZONE', 'America/New_York'))

class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True,related_name='clients_user')
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nom = models.CharField(max_length=255)
    prenom = models.CharField(max_length=255)
    tel = models.CharField(max_length=15, unique=True)
    email = models.CharField(max_length=255, unique=True)
    date_naissance = models.CharField(max_length=255, blank=True, null=True)
    lieu_naissance = models.CharField(max_length=255, blank=True, null=True)
    sexe = models.CharField(max_length=1, choices=[('M', 'Masculin'), ('F', 'Féminin')])
    adresse = models.CharField(max_length=255, blank=True, null=True)
    statut = models.CharField(max_length=255, blank=True, null=True)
    username = models.CharField(max_length=255, blank=True, null=True)
    password = models.CharField(max_length=255)
    pass_send = models.CharField(max_length=255, blank=True, null=True)
    image = models.ImageField(upload_to='customers_imgs/', default='default.jpg')
    created_at = models.DateTimeField(auto_now_add=True)  
    updated_at=models.DateField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    isActive=models.BooleanField(default=True)
    etat = models.CharField(
        max_length=10,
        choices=[('temporaire', 'Temporaire'), ('final', 'Final')],
        default='temporaire'
    )
    

    def save(self, *args, **kwargs):
        # Générer un email basé sur le téléphone si aucun email n'est fourni
        if not self.email and self.tel:
            self.email = f"{self.tel}@example.com"

        # Générer automatiquement le username
        if not self.username and self.prenom and self.tel:
            self.username = f"{self.prenom[-3:]}{self.tel[-4:]}"  # Fin du prénom + 4 derniers chiffres du tel

        if  self.pk:  # Si l'objet est nouveau
            # Générer un nouveau mot de passe
            password_length = 8
            chars = string.ascii_letters + string.digits + string.punctuation
            new_password = get_random_string(password_length, chars)
            self.pass_send = new_password  # Stocker le mot de passe non haché
            self.password = make_password(new_password)  # Hacher le mot de passe
            print(new_password)
        else:  # Si l'objet existe déjà
            # Vérifier si le mot de passe a été modifié
            try:
                old_instance = Client.objects.get(pk=self.pk)
                if self.password != old_instance.password:
                    self.password = make_password(self.password)
            except Client.DoesNotExist:
                pass  # Ignorer si l'objet n'existe pas (rare cas d'erreur)

        super().save(*args, **kwargs)

    def update_fields(self, **fields):
        """
        Méthode pour mettre à jour certains champs sans toucher aux champs sensibles.
        """
        # Filtrer les champs sensibles pour éviter toute modification
        excluded_fields = ['password', 'pass_send','user','created_by']
        for field, value in fields.items():
            if field not in excluded_fields and hasattr(self, field):
                setattr(self, field, value)

        # Sauvegarder uniquement les champs mis à jour
        self.save(update_fields=fields.keys())
    def check_password(self, password):
        return django_check_password(password, self.password)

    def __str__(self):
        return f"{self.nom} {self.prenom} ({self.etat})"

class Compte(models.Model):
    DUREE_CHOICES=[
        ('6', '6 Mois'), 
        ('9', '9 Mois'), 
        ('12', '12 Mois'), 
        ('N/A', 'N/A')
    ]
    TYPE_CHOICES = [
        ('SOL', 'Sol'),
        ('BS', 'Bousanm'),
    ]
    DEVISE_CHOICES =[
        ('HTG', 'HTG'),
        ('USD', 'USD'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    code = models.CharField(max_length=9, unique=True)
    type_compte = models.CharField(max_length=255,choices=TYPE_CHOICES)
    solde_PL = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    solde_M = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    solde_S = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    solde_BS = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    devise = models.CharField(max_length=10, choices=DEVISE_CHOICES,default='HTG')
    etat = models.CharField(max_length=20, choices=[('Actif', 'Actif'), ('Inactif', 'Inactif')], default="Actif")
    Online_Created=models.BooleanField(default=False)
    dureeP=models.CharField(max_length=10, default='N/A')
    dureeM=models.CharField(max_length=10, choices=DUREE_CHOICES, default='N/A')
    interet = models.DecimalField(max_digits=5, decimal_places=2,default=0.0)
    date_debutP = models.DateField(blank=True, null=True)  
    date_debutM = models.DateField(blank=True, null=True)  
    date_fin = models.DateField(blank=True, null=True)

    nb_main = models.DecimalField(decimal_places=2, max_digits=4, blank=True, null=True)
    sol = models.IntegerField(blank=True, null=True)
    montant_jours = models.IntegerField(blank=True, null=True)  # Calculé automatiquement

    next_run_time = models.DateTimeField(null=True, blank=True, default=None)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(blank=False, null=False)
    updated_at = models.DateTimeField(blank=False, null=False)

    def save(self, *args, **kwargs):
        if not self.code:
            if self.type_compte == 'BS':
                prefix = '500'
            elif self.type_compte == 'SOL':
                prefix = '300'
            else:
                raise ValueError("Invalid account type")

            compte_counter, created = CompteCounter.objects.get_or_create(type=self.type_compte, defaults={'value': 24000})
            compte_counter.value += 1
            compte_counter.save()
            num_al = random.randint(1, 9)
            self.code = f"{prefix}{num_al}{compte_counter.value:05d}"
        if self.type_compte=="SOL" and self.sol and self.nb_main:
    # Calculer le montant_jours
            self.montant_jours = self.nb_main * self.sol

        local_tz = get_local_timezone()
        now = timezone.now().astimezone(local_tz)
        if not self.created_at:
            self.created_at = now
        self.updated_at = now
        super(Compte, self).save(*args, **kwargs)

    def update_balance(self, new_balance):
        # Mettre à jour uniquement le champ balance sans appeler save()
        Compte.objects.filter(id=self.id).update(balance=new_balance)

    def __str__(self):
        return f"Compte {self.type_compte} - Solde: {self.solde}€"

class CompteCounter(models.Model):
    TYPE_CHOICES = [
        ('BS', 'Bousanm'),
    ]
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, unique=True)
    value = models.IntegerField(default=24000)
