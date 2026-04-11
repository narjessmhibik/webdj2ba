from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from embed_video.fields import EmbedVideoField



class Film(models.Model):
    GENRE_CHOICES = [
        ('action', 'Action'),
        ('comedie', 'Comédie'),
        ('drame', 'Drame'),
        ('science_fiction', 'Science-Fiction'),
        ('horreur', 'Horreur'),
        ('romance', 'Romance'),
        ('animation', 'Animation'),
        ('thriller', 'Thriller'),
        ('documentaire', 'Documentaire'),
    ]
    
    titre = models.CharField(max_length=200)
    realisateur = models.CharField(max_length=100)
    annee = models.IntegerField()
    duree = models.IntegerField(help_text="Durée en minutes")
    genre = models.CharField(max_length=20, choices=GENRE_CHOICES)
    description = models.TextField()
    prix_location = models.DecimalField(max_digits=6, decimal_places=2, default=3.99)
    affiche = models.ImageField(upload_to='affiches/', blank=True, null=True)
    
    # REMPLACER bande_annonce par url_video pour django-embed-video
    url_video = EmbedVideoField(
        verbose_name="URL de la vidéo",
        help_text="URL YouTube ou Vimeo (ex: https://www.youtube.com/watch?v=CODE)",
        blank=True,
        null=True
    )
    
    # Conserver l'ancien champ pour compatibilité ou le supprimer
    bande_annonce = models.URLField(
        verbose_name="Bande-annonce (URL alternative)",
        blank=True
    )
    
    date_ajout = models.DateTimeField(auto_now_add=True)
    est_disponible = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-date_ajout']
        verbose_name = "Film"
        verbose_name_plural = "Films"
    
    def __str__(self):
        return f"{self.titre} ({self.annee})"
    
    def get_genre_display(self):
        """Retourne le genre formaté"""
        return dict(self.GENRE_CHOICES).get(self.genre, self.genre)
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('detail_film', args=[str(self.id)])
    
    def get_prix_formatted(self):
        """Retourne le prix formaté"""
        return f"{self.prix_location}€"
    
    @property
    def a_video(self):
        """Vérifie si le film a une vidéo"""
        return bool(self.url_video or self.bande_annonce)
    
    @property
    def duree_formatted(self):
        """Formate la durée en heures et minutes"""
        heures = self.duree // 60
        minutes = self.duree % 60
        if heures > 0:
            return f"{heures}h{minutes:02d}"
        return f"{minutes}min"

class Location(models.Model):
    film = models.ForeignKey('Film', on_delete=models.CASCADE)
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE)
    date_location = models.DateTimeField(auto_now_add=True)
    date_expiration = models.DateTimeField()
    date_retour_effectif = models.DateTimeField(null=True, blank=True)
    prix_paye = models.DecimalField(max_digits=5, decimal_places=2)
    
    def __str__(self):
        return f"{self.film.titre} - {self.utilisateur.username}"
    
    @property
    def est_active(self):
        return self.date_expiration > timezone.now() and not self.date_retour_effectif
    
    @property
    def est_expiree(self):
        return self.date_expiration <= timezone.now() and not self.date_retour_effectif
    
    @property
    def temps_restant(self):
        if self.est_active:
            restant = self.date_expiration - timezone.now()
            jours = restant.days
            heures = restant.seconds // 3600
            return f"{jours}j {heures}h"
        return "Expiré"
    
    def marquer_comme_retourne(self):
        if self.est_expiree and not self.date_retour_effectif:
            self.date_retour_effectif = timezone.now()
            self.film.est_disponible = True
            self.film.save()
            self.save()

class ListeSouhaits(models.Model):
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE)
    film = models.ForeignKey(Film, on_delete=models.CASCADE)
    date_ajout = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['utilisateur', 'film']
    
    def __str__(self):
        return f"{self.utilisateur.username} - {self.film.titre}"

class Avis(models.Model):
    NOTE_CHOICES = [(i, i) for i in range(1, 6)]
    
    film = models.ForeignKey(Film, on_delete=models.CASCADE)
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE)
    note = models.IntegerField(choices=NOTE_CHOICES)
    commentaire = models.TextField(blank=True)
    date_avis = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['utilisateur', 'film']
    
    def __str__(self):
        return f"{self.utilisateur.username} - {self.film.titre} ({self.note}/5)"

# ============================================================================
# AJOUTEZ ICI LA CLASSE PaiementSimule (COPIER-COLLER LE CODE CI-DESSUS)
# ============================================================================
class PaiementSimule(models.Model):
    """Modèle pour simuler un paiement (académique uniquement)"""
    
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('reussi', 'Réussi'),
        ('echoue', 'Échoué'),
        ('annule', 'Annulé'),
    ]
    
    METHODE_CHOICES = [
        ('carte', 'Carte bancaire'),
        ('paypal', 'PayPal'),
        ('crypto', 'Cryptomonnaie'),
    ]
    
    location = models.OneToOneField(
        'Location',
        on_delete=models.CASCADE,
        related_name='paiement'
    )
    
    montant = models.DecimalField(max_digits=5, decimal_places=2)
    methode = models.CharField(max_length=20, choices=METHODE_CHOICES, default='carte')
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    reference = models.CharField(max_length=50, unique=True, blank=True)
    date_paiement = models.DateTimeField(auto_now_add=True)
    details = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-date_paiement']
        verbose_name = "Paiement simulé"
        verbose_name_plural = "Paiements simulés"
    
    def __str__(self):
        return f"Paiement #{self.reference} - {self.montant}€"
    
    def generer_reference(self):
        """Génère une référence unique de paiement"""
        import random
        import string
        if not self.reference:
            prefix = 'PAY'
            date_str = timezone.now().strftime('%Y%m%d')
            random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            self.reference = f"{prefix}-{date_str}-{random_str}"
        return self.reference
    
    def simuler_paiement(self):
        """Simule un paiement (TOUJOURS réussi pour le projet)"""
        import random
        self.generer_reference()
        
        self.statut = 'reussi'
        self.details = {
            'simulation': True,
            'message': 'Paiement simulé avec succès',
            'transaction_id': f'TXN-{random.randint(100000, 999999)}',
            'code_validation': 'SIM-ACCEPTED-2024'
        }
        
        self.save()
        return self.statut


   
trailer_video = models.FileField(
    upload_to='trailers/',
    blank=True,
    null=True,
    help_text="Vidéo de démonstration (max 50MB)"
)



class Livre(models.Model):
    titre = models.CharField(max_length=200)
    url_video = EmbedVideoField()  # Liens YouTube, Vimeo, etc.