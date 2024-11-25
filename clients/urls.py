from django.urls import path
from .views import *

urlpatterns = [
    path('', ClientCreateView.as_view(), name='create-client'),
    path('detail/<uuid:id>/', ClientDetailView.as_view(), name='client-detail'),
    path('comptes/', CompteCreateView.as_view(), name='create-compte'),
    path('<uuid:client_id>/comptes/', ClientComptesListView.as_view(), name='client-comptes'),
    path('comptes/<str:code>/', CompteDetailView.as_view(), name='compte-detail'),
path('<uuid:id>/activation/', ClientActivationView.as_view(), name='client-activation'),
path('create-account/<uuid:pk>/validate/', ValidateClientView.as_view(), name='validate-client'),
    path('api/clients/<uuid:pk>/', CancelClientView.as_view(), name='cancel-client'),
]
