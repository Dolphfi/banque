from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.crypto import get_random_string
from django.contrib.auth.hashers import make_password
import string

from .models import Client


@receiver(pre_save, sender=Client)
def generate_password(sender, instance, **kwargs):
    # Vérifier si l'objet est nouveau (instance sans clé primaire)
    if not instance.pk:
        # Générer un mot de passe aléatoire
        password_length = 8
        chars = string.ascii_letters + string.digits + string.punctuation
        new_password = get_random_string(password_length, chars)

        # Attribuer le mot de passe généré
        instance.pass_send = new_password  # Mot de passe en clair
        instance.password = make_password(new_password)  # Mot de passe haché

        print(f"Nouveau mot de passe pour {instance.nom} : {new_password}")
