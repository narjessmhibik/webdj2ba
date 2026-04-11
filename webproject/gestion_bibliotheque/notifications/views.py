from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Notification

@login_required
def mes_notifications(request):
    notifications = Notification.objects.filter(utilisateur=request.user).order_by('-date_creation')
    
    # Marquer comme lues quand on consulte
    notifications.filter(est_lue=False).update(est_lue=True)
    
    return render(request, 'notifications/mes_notifications.html', {
        'notifications': notifications
    })

@login_required
def marquer_comme_lue(request, notification_id):
    notification = Notification.objects.get(id=notification_id, utilisateur=request.user)
    notification.est_lue = True
    notification.save()
    return redirect('mes_notifications')

@login_required
def marquer_toutes_lues(request):
    Notification.objects.filter(utilisateur=request.user, est_lue=False).update(est_lue=True)
    return redirect('mes_notifications')