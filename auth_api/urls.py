from django.urls import path
from .views import RegisterView, LoginView, LogoutView, ProfileView, SessionDebugView

urlpatterns = [
    path('', LoginView.as_view(), name='login'),
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('debug-session/', SessionDebugView.as_view(), name='debug_session'),
]