def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        nom = request.POST.get('nom', '')
        prenom = request.POST.get('prenom', '')
        telephone = request.POST.get('telephone', '')
        
        # Vérifications existantes
        if User.objects.filter(username=username).exists():
            messages.error(request, "Ce nom d'utilisateur est déjà pris.")
            return render(request, 'registration/register.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, "Cet email est déjà utilisé.")
            return render(request, 'registration/register.html')
        
        if password1 != password2:
            messages.error(request, "Les mots de passe ne correspondent pas.")
            return render(request, 'registration/register.html')
        
        # Création de l'utilisateur
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1,
                first_name=prenom,
                last_name=nom
            )
            
            # Création manuelle du profil
            from votre_app.models import ProfilUtilisateur  # Importez ici
            ProfilUtilisateur.objects.create(
                user=user,
                nom=nom,
                prenom=prenom,
                email=email,
                telephone=telephone
            )
            
            messages.success(request, "Compte créé avec succès !")
            return redirect('login')
            
        except Exception as e:
            messages.error(request, f"Erreur: {str(e)}")
            return render(request, 'registration/register.html')
    
    return render(request, 'registration/register.html')