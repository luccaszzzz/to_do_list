from django.urls import path
from .views import (
    RegisterView, LoginView, LogoutView, 
    ProfileView, UpdateProfileView, ChangePasswordView, DeleteAccountView,
)

urlpatterns = [
    # Autenticação
    path('', LoginView.as_view(), name='login'),
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('logout/', LogoutView.as_view(), name='logout'),
    
    # Perfil
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/update/', UpdateProfileView.as_view(), name='update_profile'),
    path('profile/change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('profile/delete/', DeleteAccountView.as_view(), name='delete_account'),   
]