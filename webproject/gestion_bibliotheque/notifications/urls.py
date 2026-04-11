from django.urls import path
from . import views

urlpatterns = [
    path('', views.mes_notifications, name='mes_notifications'),
    path('<int:notification_id>/marquer-lue/', views.marquer_comme_lue, name='marquer_comme_lue'),
    path('marquer-toutes-lues/', views.marquer_toutes_lues, name='marquer_toutes_lues'),
    # path('marquer-toutes-lues/', views.marquer_toutes_lues, name='marquer_toutes_lues'),  # Commentez pour l'instant
]