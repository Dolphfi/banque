from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from api.views import *


urlpatterns = [
    path('login/', LoginView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(),name='token_refresh'),
    path('register/', RegisterView.as_view(),name='auth_register'),
    path('user/create/', UserCreateView.as_view(),name='create_user'),
    path('user/', UserCreateView.as_view(),name='list_user'),
    path('user/<int:pk>/', UserDetailView.as_view(), name='update_delete_user'),
    path('user/profile/<int:pk>/', UserDetailView.as_view(), name='profile_user'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset_password'),
    path('reset-password/<str:uidb64>/<str:token>/', ResetPasswordView.as_view(), name='reset_password_confirm'),
    path('activate-deactivate-user/<int:user_id>/', ActivateDeactivateUser.as_view(), name='activate_deactivate_user'),
    
    ]