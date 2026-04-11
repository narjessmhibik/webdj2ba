from django.utils import timezone
from .models import Notification
from bibliotheque.models import Location

def creer_notification_location(location):
    """
    Crée une notification de confirmation de location
    """
    message = f"🎬 Vous avez loué '{location.film.titre}'. Accès valable 48h."
    
    notification = Notification.objects.create(
        utilisateur=location.utilisateur.user,
        type_notification='location',
        message=message,
        film=location.film
    )
    
    return notification

def envoyer_notification_email(location, notification):
    """
    Envoie un email de confirmation de location
    (À adapter avec ton système d'emails)
    """
    from django.core.mail import send_mail
    from django.template.loader import render_to_string
    
    sujet = f"🎬 Location confirmée - {location.film.titre}"
    
    message_html = f"""
    <!DOCTYPE html>
    <html>
    <body>
        <h2>Location confirmée !</h2>
        <p>Bonjour {location.utilisateur.user.first_name},</p>
        
        <div style="background: #f0f8ff; padding: 15px; border-radius: 5px;">
            <p><strong>Film :</strong> {location.film.titre}</p>
            <p><strong>Accès :</strong> Valable 48 heures</p>
            <p><strong>Date de location :</strong> {timezone.now().strftime('%d/%m/%Y à %H:%M')}</p>
        </div>
        
        <p>Vous pouvez maintenant regarder le film depuis votre espace personnel.</p>
        <p>Bon film ! 🍿</p>
    </body>
    </html>
    """
    
    # Envoyer l'email (à décommenter quand tu seras prêt)
    # send_mail(
    #     sujet,
    #     strip_tags(message_html),  # Version texte
    #     'noreply@locfilms.com',
    #     [location.utilisateur.user.email],
    #     html_message=message_html
    # )