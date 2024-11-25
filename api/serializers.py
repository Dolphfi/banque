from api.models import *
from django.contrib.auth.password_validation import validate_password
from clients.models import Client,Compte
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import ValidationError
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.core.files.base import ContentFile
from django.conf import settings
import os
User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'role','image']

class AccountsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ['id', 'num_compte', 'email', 'username']

# class LoginSerializer(serializers.Serializer):
#     identifier = serializers.CharField()  # Champ unique pour username, tel, email, surnom
#     password = serializers.CharField(write_only=True)

#     def validate(self, data):
#         identifier = data.get('identifier')
#         password = data.get('password')

#         user = None

#         # Authentification par nom d'utilisateur
#         user = authenticate(username=identifier, password=password)

#         # Authentification par numéro de téléphone, surnom ou email si l'authentification par username échoue
#         accounts = []
        
#         if not user:
#             # Recherche dans les comptes Accounts
#             accounts = Client.objects.filter(username=identifier) | Client.objects.filter(tel=identifier) | Client.objects.filter(email=identifier)
            
#         # Vérification dans les comptes Accounts
#         for account in accounts:
#             if account.etat.lower() != 'actif':
#                 continue  # Passer au compte suivant s'il n'est pas actif
            
#             if account.check_password(password):
#                 user, created = User.objects.get_or_create(
#                     email=account.email,
#                     defaults={
#                         'username': account.username,
#                         'is_active': True,
#                         'is_staff': False,
#                         'is_superuser': False,
#                         'role': 'User'
#                     }
#                 )

#                 if not created:
#                     user.username = account.username
#                     user.set_password(password)  # Ne pas oublier de hasher le mot de passe
#                     user.save()

#                 break  # Compte authentifié avec succès, sortir de la boucle
#         if not user:
#             raise ValidationError("Unable to log in with provided credentials.")

#         # Vérification finale de l'état de l'utilisateur
#         if not user.is_active:
#             raise ValidationError("This user is not active.")

#         data['user'] = user
#         return data
    
#     def get_token(self, user):
#         refresh = RefreshToken.for_user(user)
#         user_data = UserSerializer(user).data

#         try:
#             account = Compte.objects.get(client=user.id)
#             if account.etat.lower() == 'actif':
#                 user_data.update({
#                     'code': account.code,
#                     'type': account.type_compte,
#                 })
#             else:
#                 raise ValidationError("This user is not active.")
#         except Client.DoesNotExist:
#             pass

#         return {
#             'refresh': str(refresh),
#             'access': str(refresh.access_token),
#             'user': user_data
#         }

class LoginSerializer(serializers.Serializer):
    identifier = serializers.CharField()  # Pour username, tel ou email
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        identifier = data.get('identifier')
        password = data.get('password')

        # Vérification pour les utilisateurs Admin
        user = User.objects.filter(username=identifier).first() or \
              User.objects.filter(email=identifier).first()

        if user:
            # Vérifier le mot de passe de l'utilisateur Admin
            if not user.check_password(password):
                raise serializers.ValidationError("Identifiant ou mot de passe incorrect.")
            
            # Si c'est un admin, retourner ses informations
            if user.role.lower() == 'admin':
                data['user'] = user
                data['compte'] = None
                return data

        # Vérification pour les clients
        client = Client.objects.filter(username=identifier).first() or \
                 Client.objects.filter(tel=identifier).first() or \
                 Client.objects.filter(email=identifier).first()

        if not client:
            raise serializers.ValidationError("Identifiant ou mot de passe incorrect.")

        if client.etat.lower() != 'final' or not client.isActive:
            raise serializers.ValidationError("Le compte client n'est pas actif.")

        # Vérifier le mot de passe du client
        if not client.user or not client.user.check_password(password):
            raise serializers.ValidationError("Identifiant ou mot de passe incorrect.")

        # Recherche d'un compte actif pour le client
        compte = Compte.objects.filter(client=client, etat__iexact='Actif').first()
        if not compte:
            raise serializers.ValidationError("Aucun compte actif trouvé pour ce client.")

        # Ajouter l'utilisateur et le compte aux données validées
        data['user'] = client.user
        data['compte'] = compte
        return data

    def get_token(self, user):
        # Créer le token de rafraîchissement et le token d'accès pour l'utilisateur
        refresh = RefreshToken.for_user(user)

        # Payload personnalisé pour le token
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'id': user.id,
                'username': user.username,
                'role': user.role
            }
        }


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['username'] = user.username
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name
        token['role'] = user.role
        token['image'] = str(user.image.url)

        return token

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password2 = serializers.CharField(
        write_only=True, required=True
    )

    class Meta:
        model = User
        fields = ['first_name','last_name','email', 'username', 'password', 'password2']

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )

        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')  # Remove 'password2' from validated_data
        validated_data['password'] = make_password(validated_data.get('password'))
        return super().create(validated_data)

class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','first_name','last_name','email','username','password','role','is_staff','is_superuser','is_active','image']
        extra_kwargs = {
            'password': {'write_only': True},  # Ne pas afficher le mot de passe lors de la sérialisation
            'is_active': {'read_only': True},
            'is_staff': {'read_only': True},
            'is_superuser': {'read_only': True},
            }
        
    def create(self, validated_data):
        password = validated_data.pop('password')
        image = validated_data.pop('image', None)  # Récupérer l'image ou None si elle n'est pas présente
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        if image:  # Vérifier si une image a été fournie
            user.image = image
            user.save()
        return user

class UserUpdateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ['id','first_name','last_name','email','username','role','password','image']
        extra_kwargs = {
            'is_active': {'read_only': True},
            'is_staff': {'read_only': True},
            'role': {'read_only': True},
            'is_superuser': {'read_only': True},
        }

    def update(self, instance, validated_data):
        password = validated_data.get('password')
        image = validated_data.pop('image', None)

        # Mettre à jour les champs avec les données validées uniquement s'ils ne sont pas vides
        for attr, value in validated_data.items():
            if value != '':
                setattr(instance, attr, value)

        # Vérifier si le mot de passe est fourni et s'il est différent de l'ancien mot de passe
        if password and password != '':
            instance.password = make_password(password)

        instance.save()

        if image:
            instance.image = image
            instance.save()

        return instance
 
class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("No user found with this email address.")
        return value

class ResetPasswordSerializer(serializers.Serializer):
    uidb64 = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField()
    confirm_password = serializers.CharField()

    def validate(self, data):
        uidb64 = data.get('uidb64')
        token = data.get('token')
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')

        # Validate that the new password and confirm password match
        if new_password != confirm_password:
            raise serializers.ValidationError("The new password and confirm password do not match.")

        # Validate the uidb64 and token
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError("Invalid uidb64 or token.")

        if not default_token_generator.check_token(user, token):
            raise serializers.ValidationError("Invalid token for this user.")

        return data