from api.models import *
from api.serializers import *
from rest_framework.permissions import AllowAny,IsAuthenticated,IsAdminUser
from rest_framework.decorators import api_view,permission_classes
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics,status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes,force_str
from django.core.mail import send_mail
from rest_framework.exceptions import PermissionDenied
from django.core.mail import EmailMessage
from django.template.loader import render_to_string


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        # Générer le token
        tokens = serializer.get_token(user)

        return Response(tokens, status=status.HTTP_200_OK)
    
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated,IsAdminUser])
def getRoutes(request):
    routes = [
        '/api/token/',
        '/api/register/',
    '/api/token/refresh/'
    ]
    return Response(routes)

@permission_classes([IsAuthenticated,IsAdminUser])
class UserCreateView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    
@permission_classes([IsAuthenticated,IsAdminUser])
class UserDetailView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserUpdateSerializer

# class ForgotPasswordView(APIView):
#     def post(self, request):
#         serializer = ForgotPasswordSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         email = serializer.validated_data['email']
        
#         try:
#             # Rechercher l'utilisateur dans la table User
#             user = User.objects.get(email=email)
#         except User.DoesNotExist:
#             try:
#                 # Rechercher l'utilisateur dans la table Accounts
#                 account = Accounts.objects.get(email=email)
#                 if account.etat.lower() == 'actif':  # Vérifiez si le compte est actif
#                     # Synchroniser avec la table User
#                     user, created = User.objects.get_or_create(
#                         username=account.username,
#                         email=account.email,
#                         defaults={
#                             'is_active': True,
#                             'is_staff': False,
#                             'is_superuser': False,
#                             'role': 'User'
#                         }
#                     )
#                     if not created:
#                         user.set_password(account.password)
#                         user.save()
#                 else:
#                     return Response({'error': "Votre compte n'est pas actif."}, status=status.HTTP_400_BAD_REQUEST)
#             except Accounts.DoesNotExist:
#                 return Response({'error': "Impossible de trouver un utilisateur avec cet email."}, status=status.HTTP_400_BAD_REQUEST)
        
#         # Generate token
#         token = default_token_generator.make_token(user)

#         # Send email with reset link
#         reset_link = f"https://bousanm.netlify.app/reset-password/{urlsafe_base64_encode(force_bytes(user.pk))}/{token}/"
#         message = f"Click the following link to reset your password: {reset_link}"
#         send_mail('Password Reset', message, 'info@ziginvestment.com', [email])

#         return Response({'message': 'Password reset link sent successfully'})

# class ForgotPasswordView(APIView):
#     def post(self, request):
#         serializer = ForgotPasswordSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         email = serializer.validated_data['email']
        
#         try:
#             # Rechercher l'utilisateur dans la table User
#             user = User.objects.get(email=email)
#         except User.DoesNotExist:
#             try:
#                 # Rechercher l'utilisateur dans la table Accounts
#                 account = Accounts.objects.get(email=email)
#                 if account.etat.lower() == 'actif':  # Vérifiez si le compte est actif
#                     # Synchroniser avec la table User
#                     user, created = User.objects.get_or_create(
#                         username=account.username,
#                         email=account.email,
#                         defaults={
#                             'is_active': True,
#                             'is_staff': False,
#                             'is_superuser': False,
#                             'role': 'User'
#                         }
#                     )
#                     if not created:
#                         user.set_password(account.password)
#                         user.save()
#                 else:
#                     return Response({'error': "Votre compte n'est pas actif."}, status=status.HTTP_400_BAD_REQUEST)
#             except Accounts.DoesNotExist:
#                 return Response({'error': "Impossible de trouver un utilisateur avec cet email."}, status=status.HTTP_400_BAD_REQUEST)

#         # Generate token
#         token = default_token_generator.make_token(user)

#         # Create reset link
#         reset_link = f"https://bousanm.com/reset-password/{urlsafe_base64_encode(force_bytes(user.pk))}/{token}/"

#         # Load HTML template and render it with the reset link
#         context = {
#             'reset_link': reset_link,
#             'first_name': account.prenom if 'account' in locals() else user.first_name,
#             'last_name': account.nom if 'account' in locals() else user.last_name,
#             'logo_url': request.build_absolute_uri(settings.MEDIA_URL + 'logo1.png'),
#             'logo1_url': request.build_absolute_uri(settings.MEDIA_URL + 'Zig.png')
#         }
#         html_content = render_to_string('emails/reset_password_email.html', context)

#         # Send email with HTML content
#         email_message = EmailMessage(
#             'Réinitialisation de mot de passe',
#             html_content,
#             'info@ziginvestment.com',
#             [email],
#         )
#         email_message.content_subtype = 'html'  # This is necessary to send HTML email

#         email_message.send()

#         return Response({'message': 'Lien de réinitialisation de mot de passe envoyé avec succès'})

# class ResetPasswordView(APIView):
#     def post(self, request):
#         serializer = ResetPasswordSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         uidb64 = serializer.validated_data['uidb64']
#         token = serializer.validated_data['token']
#         new_password = serializer.validated_data['new_password']
#         confirm_password = serializer.validated_data['confirm_password']
#         # Logic to reset password
#         return Response({'message': 'Password reset successfully'})
#     def post(self, request, uidb64, token):
#         try:
#             uid = force_str(urlsafe_base64_decode(uidb64))
#             user = User.objects.get(pk=uid)
            
#             if default_token_generator.check_token(user, token):
#                 new_password = request.data.get('new_password')
#                 confirm_password = request.data.get('confirm_password')
                
#                 if new_password == confirm_password:
#                     user.set_password(new_password)
#                     user.save()
#                     return Response({'message': 'Password reset successfully'})
#                 else:
#                     return Response({'error': 'Passwords do not match'}, status=status.HTTP_400_BAD_REQUEST)
#             else:
#                 return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)
#         except (TypeError, ValueError, OverflowError, User.DoesNotExist):
#             return Response({'error': 'Invalid UID or token'}, status=status.HTTP_400_BAD_REQUEST)

class ForgotPasswordView(APIView):
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        
        try:
            # Rechercher l'utilisateur dans la table User
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            try:
                # Rechercher l'utilisateur dans la table Accounts
                account = Accounts.objects.get(email=email)
                if account.etat.lower() == 'actif':  # Vérifiez si le compte est actif
                    # Synchroniser avec la table User
                    user, created = User.objects.get_or_create(
                        username=account.username,
                        email=account.email,
                        defaults={
                            'is_active': True,
                            'is_staff': False,
                            'is_superuser': False,
                            'role': 'User'
                        }
                    )
                    if not created:
                        user.set_password(account.password)
                        user.save()
                else:
                    return Response({'error': "Votre compte n'est pas actif."}, status=status.HTTP_400_BAD_REQUEST)
            except Accounts.DoesNotExist:
                return Response({'error': "Impossible de trouver un utilisateur avec cet email."}, status=status.HTTP_400_BAD_REQUEST)

        # Generate token
        token = default_token_generator.make_token(user)

        # Create reset link
        reset_link = f"https://bousanm.com/reset-password/{urlsafe_base64_encode(force_bytes(user.pk))}/{token}/"

        # Load HTML template and render it with the reset link
        context = {
            'reset_link': reset_link,
            'first_name': account.prenom if 'account' in locals() else user.first_name,
            'last_name': account.nom if 'account' in locals() else user.last_name,
            'logo_url': request.build_absolute_uri(settings.MEDIA_URL + 'logo1.png'),
            'logo1_url': request.build_absolute_uri(settings.MEDIA_URL + 'Zig.png')
        }
        html_content = render_to_string('emails/reset_password_email.html', context)

        # Send email with HTML content
        email_message = EmailMessage(
            'Réinitialisation de mot de passe',
            html_content,
            'info@ziginvestment.com',
            [email],
        )
        email_message.content_subtype = 'html'  # This is necessary to send HTML email

        email_message.send()

        return Response({'message': 'Lien de réinitialisation de mot de passe envoyé avec succès'})

class ResetPasswordView(APIView):
    def post(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
            
            if default_token_generator.check_token(user, token):
                new_password = request.data.get('new_password')
                confirm_password = request.data.get('confirm_password')
                
                if new_password == confirm_password:
                    user.set_password(new_password)
                    user.save()
                    return Response({'message': 'Mot de passe réinitialisé avec succès'})
                else:
                    return Response({'error': 'Les mots de passe ne correspondent pas'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'error': 'Token invalide'}, status=status.HTTP_400_BAD_REQUEST)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            # Si l'utilisateur n'est pas trouvé dans User, vérifier dans Accounts
            try:
                account = Accounts.objects.get(pk=uid)
                
                if default_token_generator.check_token(account, token):
                    new_password = request.data.get('new_password')
                    confirm_password = request.data.get('confirm_password')
                    
                    if new_password == confirm_password:
                        account.set_password(new_password)
                        account.save()
                        return Response({'message': 'Mot de passe réinitialisé avec succès'})
                    else:
                        return Response({'error': 'Les mots de passe ne correspondent pas'}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({'error': 'Token invalide'}, status=status.HTTP_400_BAD_REQUEST)
            except (TypeError, ValueError, OverflowError, Accounts.DoesNotExist):
                return Response({'error': 'UID ou token invalide'}, status=status.HTTP_400_BAD_REQUEST)

@permission_classes([IsAuthenticated, IsAdminUser])
class ActivateDeactivateUser(APIView):
    def post(self, request, user_id):
        if request.user.id == user_id:
            raise PermissionDenied("You cannot deactivate your own account.")

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        user.is_active = not user.is_active
        user.save()

        message = "Account activated." if user.is_active else "Account deactivated."
        return Response({"message": message})
