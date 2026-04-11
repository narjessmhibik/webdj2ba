# bibliotheque/management/commands/gerer_retours_automatiques.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from bibliotheque.models import Location

class Command(BaseCommand):
    help = 'Gère les retours automatiques des locations expirées'

    def handle(self, *args, **options):
        locations_expirees = Location.objects.filter(
            date_expiration__lte=timezone.now(),
            date_retour_effectif__isnull=True
        )
        
        for location in locations_expirees:
            location.marquer_comme_retourne()
            self.stdout.write(f"📍 Film retourné: {location.film.titre}")
        
        self.stdout.write(self.style.SUCCESS(f'✅ {locations_expirees.count()} locations gérées automatiquement'))