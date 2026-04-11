from django.contrib import admin
from .models import Film, Location, ListeSouhaits, Avis

@admin.register(Film)
class FilmAdmin(admin.ModelAdmin):
    list_display = ('titre', 'realisateur', 'annee', 'genre', 'prix_location', 'est_disponible')
    list_filter = ('genre', 'annee', 'est_disponible')
    search_fields = ('titre', 'realisateur')
    list_editable = ('prix_location', 'est_disponible')

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = (
        'film', 
        'utilisateur', 
        'date_location', 
        'date_expiration',  # ✅ Utiliser le bon champ
        'prix_paye',
    )
    list_filter = (
        'date_location',
        'date_expiration',
    )
    search_fields = ('film__titre', 'utilisateur__username')

@admin.register(ListeSouhaits)
class ListeSouhaitsAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'film', 'date_ajout')
    list_filter = ('date_ajout',)

@admin.register(Avis)
class AvisAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'film', 'note', 'date_avis')
    list_filter = ('note', 'date_avis')
    search_fields = ('utilisateur__username', 'film__titre', 'commentaire')
    readonly_fields = ('date_avis',)