from django.db import models
from django.contrib.auth.models import User

class Notification(models.Model):
    TYPE_CHOICES = [
        ('location', 'Confirmation de location'),  # ← NOUVEAU TYPE
        ('nouveau_film', 'Nouveau film disponible'),
        ('promotion', 'Promotion spéciale'),
        ('recommandation', 'Recommandation personnalisée'),
        # SUPPRIMER 'retard' et 'rappel'
    ]
    
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE)
    type_notification = models.CharField(max_length=20, choices=TYPE_CHOICES)
    message = models.TextField()
    date_creation = models.DateTimeField(auto_now_add=True)
    est_lue = models.BooleanField(default=False)
    film = models.ForeignKey('bibliotheque.Film', on_delete=models.CASCADE, null=True, blank=True)
    
    def __str__(self):
        return f"{self.utilisateur.username} - {self.type_notification}"
    
    class Meta:
        app_label = 'notifications'