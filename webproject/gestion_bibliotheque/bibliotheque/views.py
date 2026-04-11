from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from django.db.models import Avg, Count, Q, Sum  
from django.contrib import messages
from django.http import HttpResponse  # Si vous utilisez debug_date
from .models import Film, Location, ListeSouhaits, Avis, PaiementSimule 
from notifications.services import creer_notification_location, envoyer_notification_email
from .forms import AvisForm, FormulairePaiementSimule

def detail_film(request, film_id):
    film = get_object_or_404(Film, id=film_id)
    avis_list = Avis.objects.filter(film=film).order_by('-date_avis')
    
    # Vérifier si l'utilisateur a déjà donné son avis
    user_avis = None
    dans_liste_souhaits = False
    user_has_active_rental = False
    active_location_id = None  # ✅ NOUVEAU : ID de la location active
    
    if request.user.is_authenticated:
        user_avis = Avis.objects.filter(film=film, utilisateur=request.user).first()
        dans_liste_souhaits = ListeSouhaits.objects.filter(
            film=film, 
            utilisateur=request.user
        ).exists()
        
        # ✅ CORRECTION : Récupérer aussi l'ID de la location active
        active_location = Location.objects.filter(
            film=film,
            utilisateur=request.user,
            date_expiration__gt=timezone.now(),
            date_retour_effectif__isnull=True
        ).first()
        
        if active_location:
            user_has_active_rental = True
            active_location_id = active_location.id  # ✅ Stocker l'ID pour le template
    
    # Gestion du formulaire d'avis
    if request.method == 'POST' and request.user.is_authenticated:
        form = AvisForm(request.POST)
        if form.is_valid():
            # Vérifier si l'utilisateur a déjà donné son avis
            existing_avis = Avis.objects.filter(film=film, utilisateur=request.user).first()
            
            if existing_avis:
                # Mettre à jour l'avis existant
                existing_avis.note = form.cleaned_data['note']
                existing_avis.commentaire = form.cleaned_data['commentaire']
                existing_avis.save()
                messages.success(request, 'Votre avis a été mis à jour avec succès!')
            else:
                # Créer un nouvel avis
                avis = form.save(commit=False)
                avis.film = film
                avis.utilisateur = request.user
                avis.save()
                messages.success(request, 'Merci pour votre avis!')
            
            return redirect('detail_film', film_id=film.id)
        else:
            messages.error(request, 'Veuillez corriger les erreurs ci-dessous.')
    else:
        if user_avis:
            # Pré-remplir le formulaire avec l'avis existant
            form = AvisForm(instance=user_avis)
        else:
            form = AvisForm()
    
    # Calculer la note moyenne
    note_moyenne = None
    if avis_list:
        note_moyenne = sum(avis.note for avis in avis_list) / len(avis_list)
    print(f"URL vidéo du film: {film.url_video}")
    context = {
        'film': film,
        'avis_list': avis_list,
        'form': form,
        'user_avis': user_avis,
        'note_moyenne': note_moyenne,
        'total_avis': len(avis_list),
        'dans_liste_souhaits': dans_liste_souhaits,
        'user_has_active_rental': user_has_active_rental,
        'active_location_id': active_location_id,  # ✅ NOUVEAU : ID de la location
        'now': timezone.now(),
    }
    return render(request, 'bibliotheque/detail_film.html', context)


@login_required
def louer_film(request, film_id):
    # ✅ TOUS les films sont disponibles maintenant
    film = get_object_or_404(Film, id=film_id)
    
    # Vérifier si l'utilisateur n'a pas déjà une location active pour CE film
    location_active = Location.objects.filter(
        film=film, 
        utilisateur=request.user,
        date_expiration__gt=timezone.now(),
        date_retour_effectif__isnull=True
    ).exists()
    
    if not location_active:
        # Créer la location avec expiration automatique dans 48h
        location = Location.objects.create(
            film=film,
            utilisateur=request.user,
            date_expiration=timezone.now() + timedelta(hours=48),
            prix_paye=film.prix_location
        )
        
        # ✅ PLUS BESOIN DE MODIFIER est_disponible
        # Le film reste disponible pour les autres utilisateurs
        
        # Notification
        try:
            creer_notification_location(location)
            envoyer_notification_email(location)
            messages.success(request, f'Film "{film.titre}" loué avec succès! Accès valable 48h.')
        except Exception as e:
            print(f"Erreur notification: {e}")
            messages.success(request, f'Film "{film.titre}" loué avec succès! (Notification non envoyée)')
            
    else:
        messages.info(request, f'Vous avez déjà une location active pour "{film.titre}"!')
    
    return redirect('mes_locations')


@login_required
def mes_locations(request):
    from django.utils import timezone
    
    locations = Location.objects.filter(utilisateur=request.user).order_by('-date_location')
    
    # ✅ DEBUG dans la console
    print("=== DEBUG DATES ===")
    print(f"Maintenant: {timezone.now()}")
    for loc in locations:
        print(f"{loc.film.titre}: {loc.date_expiration} > {timezone.now()} = {loc.date_expiration > timezone.now()}")
    
    context = {
        'locations': locations,
        'now': timezone.now(),  # ✅ IMPORTANT : passer l'heure actuelle au template
    }
    return render(request, 'bibliotheque/mes_locations.html', context)


@login_required
def ajouter_liste_souhaits(request, film_id):
    film = get_object_or_404(Film, id=film_id)
    
    if not ListeSouhaits.objects.filter(film=film, utilisateur=request.user).exists():
        ListeSouhaits.objects.create(film=film, utilisateur=request.user)
        messages.success(request, f'"{film.titre}" ajouté à votre liste de souhaits!')
    else:
        messages.info(request, f'"{film.titre}" est déjà dans votre liste de souhaits!')
    
    return redirect('detail_film', film_id=film_id)


@login_required
def supprimer_liste_souhaits(request, film_id):
    film = get_object_or_404(Film, id=film_id)
    ListeSouhaits.objects.filter(film=film, utilisateur=request.user).delete()
    messages.info(request, f'"{film.titre}" retiré de votre liste de souhaits!')
    return redirect('ma_liste_souhaits')


@login_required
def ma_liste_souhaits(request):
    souhaits = ListeSouhaits.objects.filter(utilisateur=request.user).order_by('-date_ajout')
    return render(request, 'bibliotheque/ma_liste_souhaits.html', {'souhaits': souhaits})


def accueil(request):
    # Films récemment ajoutés + recommandations
    films_recents = Film.objects.filter(est_disponible=True).order_by('-date_ajout')[:8]
    
    # Recommandations basiques (films les mieux notés)
    films_populaires = Film.objects.annotate(
        note_moyenne=Avg('avis__note'),
        nb_avis=Count('avis')
    ).filter(nb_avis__gte=1).order_by('-note_moyenne')[:6]
    
    # ✅ CORRECTION : Supprimer le filtre 'en_vedette' qui n'existe pas
    # Remplacer par des films populaires ou récents
    films_en_vedette = Film.objects.filter(
        est_disponible=True
    ).annotate(
        nb_locations=Count('location')
    ).order_by('-nb_locations')[:4]  # Films les plus loués
    
    context = {
        'films_recents': films_recents,
        'films_populaires': films_populaires,
        'films_en_vedette': films_en_vedette,
    }
    return render(request, 'bibliotheque/accueil.html', context)

def catalogue_films(request):
    films = Film.objects.filter(est_disponible=True)
    
    # Filtres
    genre = request.GET.get('genre')
    if genre:
        films = films.filter(genre=genre)
    
    recherche = request.GET.get('q')
    if recherche:
        films = films.filter(titre__icontains=recherche)
    
    # Trier par...
    tri = request.GET.get('tri', 'titre')
    if tri == 'date':
        films = films.order_by('-date_ajout')
    elif tri == 'prix':
        films = films.order_by('prix_location')
    elif tri == 'note':
        films = films.annotate(note_moyenne=Avg('avis__note')).order_by('-note_moyenne')
    else:
        films = films.order_by('titre')
    
    # ✅ CORRECTION : Utiliser les GENRES RÉELS de la base de données
    # Récupérer tous les genres distincts des films disponibles
    genres_disponibles = Film.objects.filter(
        est_disponible=True
    ).values_list('genre', flat=True).distinct()
    
    # Créer des tuples (value, label) avec les libellés corrects
    genres_with_labels = []
    for genre_value in genres_disponibles:
        # Trouver le libellé correspondant dans GENRE_CHOICES
        for value, label in Film.GENRE_CHOICES:
            if value == genre_value:
                genres_with_labels.append((value, label))
                break
    
    context = {
        'films': films,
        'genres': genres_with_labels,  # ✅ Maintenant les vrais genres de ta base
    }
    return render(request, 'bibliotheque/catalogue_films.html', context)

@login_required
def debug_date(request):
    from django.utils import timezone
    import datetime
    
    locations = Location.objects.filter(utilisateur=request.user)
    
    html = f"""
    <h1>Debug Dates</h1>
    <p>Heure actuelle du serveur: {timezone.now()}</p>
    <p>Heure actuelle Python: {datetime.datetime.now()}</p>
    <hr>
    """
    
    for loc in locations:
        html += f"""
        <div style="border: 1px solid #ccc; padding: 10px; margin: 10px;">
            <h3>{loc.film.titre}</h3>
            <p>Date location: {loc.date_location}</p>
            <p>Date expiration: {loc.date_expiration}</p>
            <p>Maintenant: {timezone.now()}</p>
            <p>Expiration > Maintenant: {loc.date_expiration > timezone.now()}</p>
            <p>Différence: {loc.date_expiration - timezone.now()}</p>
            <p style="color: {'green' if loc.date_expiration > timezone.now() else 'red'}">
                Statut: {'ACTIF' if loc.date_expiration > timezone.now() else 'EXPIRÉ'}
            </p>
        </div>
        """
    
    return HttpResponse(html)

@login_required
def regarder_film(request, film_id):
    film = get_object_or_404(Film, id=film_id)
    
    # Vérifier que l'utilisateur a une location active
    location_active = Location.objects.filter(
        film=film,
        utilisateur=request.user,
        date_expiration__gt=timezone.now(),
        date_retour_effectif__isnull=True
    ).first()
    
    if not location_active:
        messages.error(request, "Vous n'avez pas accès à ce film ou votre location a expiré.")
        return redirect('mes_locations')
    
    # Ici vous intégrerez votre système de streaming
    # Pour l'instant, on affiche une page de simulation
    return render(request, 'bibliotheque/regarder_film.html', {
        'film': film,
        'location': location_active
    })


@login_required
def retourner_film(request, location_id):
    location = get_object_or_404(Location, id=location_id, utilisateur=request.user)
    
    if location.date_retour_effectif:
        messages.info(request, "Ce film a déjà été retourné.")
    else:
        # Marquer comme retourné
        location.date_retour_effectif = timezone.now()
        location.save()
        
        # ❌❌❌ SUPPRIMER CES LIGNES ❌❌❌
        # film = location.film
        # film.est_disponible = True  # ⛔ À SUPPRIMER
        # film.save()  # ⛔ À SUPPRIMER
        
        messages.success(request, f'Film "{location.film.titre}" retourné avec succès!')
    
    return redirect('mes_locations')


@login_required
def historique_locations(request):
    locations = Location.objects.filter(
        utilisateur=request.user
    ).order_by('-date_location')
    
    return render(request, 'bibliotheque/historique_locations.html', {
        'locations': locations
    })


# Vue pour les films recommandés (basique)
@login_required
def films_recommandes(request):

    # Logique simple de recommandation basée sur le genre des films déjà loués
    genres_loues = Location.objects.filter(
        utilisateur=request.user
    ).values_list('film__genre', flat=True).distinct()
    
    films_recommandes = Film.objects.filter(
        est_disponible=True,
        genre__in=genres_loues
    ).exclude(
        location__utilisateur=request.user  # Exclure les films déjà loués
    )[:12]
    
    # Si pas assez de recommandations, ajouter des films populaires
    if len(films_recommandes) < 6:
        films_populaires = Film.objects.filter(est_disponible=True).annotate(
            nb_locations=Count('location')
        ).order_by('-nb_locations')[:12]
        
        # Combiner les deux listes sans doublons
        ids_deja_presents = [f.id for f in films_recommandes]
        films_supplementaires = films_populaires.exclude(id__in=ids_deja_presents)
        films_recommandes = list(films_recommandes) + list(films_supplementaires)[:12]
    
    return render(request, 'bibliotheque/films_recommandes.html', {
        'films_recommandes': films_recommandes
    })



    # Dans views.py, ajoutez :

@login_required
def initier_paiement(request, film_id):
    """Page intermédiaire avant la location avec simulation de paiement"""
    film = get_object_or_404(Film, id=film_id)
    
    # Vérifier si pas déjà loué
    location_active = Location.objects.filter(
        film=film, 
        utilisateur=request.user,
        date_expiration__gt=timezone.now(),
        date_retour_effectif__isnull=True
    ).exists()
    
    if location_active:
        messages.info(request, f'Vous avez déjà une location active pour "{film.titre}"!')
        return redirect('mes_locations')
    
    context = {
        'film': film,
        'prix': film.prix_location,
    }
    return render(request, 'bibliotheque/initier_paiement.html', context)

@login_required
def simulation_paiement(request, film_id):
    """Page de simulation de paiement - TOUJOURS réussi"""
    film = get_object_or_404(Film, id=film_id)
    
    # Vérifier si pas déjà loué
    location_active = Location.objects.filter(
        film=film, 
        utilisateur=request.user,
        date_expiration__gt=timezone.now(),
        date_retour_effectif__isnull=True
    ).exists()
    
    if location_active:
        messages.info(request, f'Vous avez déjà une location active pour "{film.titre}"!')
        return redirect('mes_locations')
    
    if request.method == 'POST':
        form = FormulairePaiementSimule(request.POST)
        
        if form.is_valid():
            # 1. Créer la location
            location = Location.objects.create(
                film=film,
                utilisateur=request.user,
                date_expiration=timezone.now() + timedelta(hours=48),
                prix_paye=film.prix_location
            )
            
            # 2. Créer le paiement simulé
            paiement = PaiementSimule.objects.create(
                location=location,
                montant=film.prix_location,
                methode=form.cleaned_data['methode']
            )
            
            # 3. Simuler le paiement (TOUJOURS réussi)
            paiement.simuler_paiement()  # ← Cette méthode est maintenant garantie réussie
            
            # Notification
            try:
                from notifications.services import creer_notification_location, envoyer_notification_email
                creer_notification_location(location)
                envoyer_notification_email(location)
            except Exception as e:
                print(f"Erreur notification: {e}")
            
            messages.success(
                request, 
                f'✅ Paiement simulé réussi ! Film "{film.titre}" loué pour 48h.'
            )
            return redirect('confirmation_paiement', reference=paiement.reference)
    else:
        form = FormulairePaiementSimule()
    
    context = {
        'film': film,
        'form': form,
        'prix': film.prix_location,
    }
    return render(request, 'bibliotheque/simulation_paiement.html', context)

@login_required
def confirmation_paiement(request, reference):
    """Page de confirmation après paiement réussi"""
    paiement = get_object_or_404(PaiementSimule, reference=reference, location__utilisateur=request.user)
    location = paiement.location
    
    context = {
        'paiement': paiement,
        'location': location,
        'film': location.film,
    }
    return render(request, 'bibliotheque/confirmation_paiement.html', context)

@login_required
def echec_paiement(request, reference):
    """Page d'échec de paiement"""
    paiement = get_object_or_404(PaiementSimule, reference=reference, location__utilisateur=request.user)
    
    context = {
        'paiement': paiement,
        'film': paiement.location.film,
    }
    return render(request, 'bibliotheque/echec_paiement.html', context)

@login_required
def historique_paiements(request):
    """Historique des paiements simulés de l'utilisateur"""
    paiements = PaiementSimule.objects.filter(
        location__utilisateur=request.user
    ).select_related('location', 'location__film').order_by('-date_paiement')
    
    context = {
        'paiements': paiements,
    }
    return render(request, 'bibliotheque/historique_paiements.html', context)

# Ajoutez cette vue dans views.py
@login_required
def historique_paiements(request):
    """Historique des paiements simulés de l'utilisateur"""
    paiements = PaiementSimule.objects.filter(
        location__utilisateur=request.user
    ).select_related('location', 'location__film').order_by('-date_paiement')
    
    # Statistiques
    paiements_reussis = paiements.filter(statut='reussi')
    paiements_echoues = paiements.filter(statut='echoue')
    total_montant = paiements_reussis.aggregate(Sum('montant'))['montant__sum']
    
    context = {
        'paiements': paiements,
        'paiements_reussis': paiements_reussis,
        'paiements_echoues': paiements_echoues,
        'total_montant': total_montant,
    }
    return render(request, 'bibliotheque/historique_paiements.html', context)