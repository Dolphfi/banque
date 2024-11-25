from django.urls import path
from .views import ClientCreateView, CompteCreateView, ValidateClientView, CancelClientView

urlpatterns = [
    path('clients/', ClientCreateView.as_view(), name='create-client'),
    path('comptes/', CompteCreateView.as_view(), name='create-compte'),
    path('api/clients/<uuid:pk>/validate/', ValidateClientView.as_view(), name='validate-client'),
    path('api/clients/<uuid:pk>/', CancelClientView.as_view(), name='cancel-client'),
]
