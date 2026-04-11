from django.urls import path
from . import views

urlpatterns = [
    path('', views.accueil, name='accueil'),
    path('catalogue/', views.catalogue_films, name='catalogue_films'),
    path('film/<int:film_id>/', views.detail_film, name='detail_film'),
    path('film/<int:film_id>/louer/', views.louer_film, name='louer_film'),
    #path('film/<int:film_id>/retourner/', views.retourner_film, name='retourner_film'),
    path('film/<int:film_id>/souhait/ajouter/', views.ajouter_liste_souhaits, name='ajouter_liste_souhaits'),
    path('film/<int:film_id>/souhait/supprimer/', views.supprimer_liste_souhaits, name='supprimer_liste_souhaits'),
    path('mes-locations/', views.mes_locations, name='mes_locations'),
    path('ma-liste-souhaits/', views.ma_liste_souhaits, name='ma_liste_souhaits'),
    path('film/<int:film_id>/regarder/', views.regarder_film, name='regarder_film'),
    path('debug-date/', views.debug_date, name='debug_date'),
        # Nouvelles URLs pour le paiement
    path('film/<int:film_id>/paiement/', views.initier_paiement, name='initier_paiement'),
    path('film/<int:film_id>/paiement/simuler/', views.simulation_paiement, name='simulation_paiement'),
    path('paiement/confirmation/<str:reference>/', views.confirmation_paiement, name='confirmation_paiement'),
    path('paiement/echec/<str:reference>/', views.echec_paiement, name='echec_paiement'),
    path('mes-paiements/', views.historique_paiements, name='historique_paiements'),

]

