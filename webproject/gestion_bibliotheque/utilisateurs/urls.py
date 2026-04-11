from django.urls import path
from . import views

#app_name = 'utilisateurs'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('logout/', views.custom_logout, name='logout'),  # ← Déconnexion personnalisée
]