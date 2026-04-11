from django.core.management.base import BaseCommand
from django.utils import timezone
from bibliotheque.models import Location
from notifications.models import Notification

class Command(BaseCommand):
    help = 'Vérifie les locations en retard et envoie des notifications'
    
    def handle(self, *args, **options):
        maintenant = timezone.now()
        
        # Locations en retard
        locations_en_retard = Location.objects.filter(
            date_retour_prevue__lt=maintenant,
            date_retour_effectif__isnull=True,
            est_en_retard=False
        )
        
        for location in locations_en_retard:
            # Marquer comme en retard
            location.est_en_retard = True
            location.save()
            
            # Créer notification
            Notification.objects.create(
                utilisateur=location.utilisateur,
                type_notification='retard',
                message=f"ATTENTION: La location du film '{location.film.titre}' est en retard ! Veuillez le retourner rapidement pour éviter des frais supplémentaires.",
                film=location.film
            )
            
            self.stdout.write(
                self.style.WARNING(f"📀 Location en retard: {location.film.titre} - {location.utilisateur.username}")
            )
        
        # Rappels pour retours proches (dans 24h)
        date_rappel = maintenant + timezone.timedelta(hours=24)
        locations_a_rappeler = Location.objects.filter(
            date_retour_prevue__lte=date_rappel,
            date_retour_prevue__gt=maintenant,
            date_retour_effectif__isnull=True
        )
        
        for location in locations_a_rappeler:
            Notification.objects.create(
                utilisateur=location.utilisateur,
                type_notification='rappel',
                message=f"RAPPEL: Le film '{location.film.titre}' doit être retourné le {location.date_retour_prevue.strftime('%d/%m/%Y')}.",
                film=location.film
            )
            
            self.stdout.write(
                self.style.SUCCESS(f"⏰ Rappel envoyé: {location.film.titre}")
            )
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ Tâche terminée: {locations_en_retard.count()} retards, {locations_a_rappeler.count()} rappels')
        )