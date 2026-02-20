from django.urls import path
from .views import DeleteAccountView

urlpatterns = [
    path('delete_account/', DeleteAccountView.as_view(), name='delete_account'),
]
