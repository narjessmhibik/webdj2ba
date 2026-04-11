from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout
from django.contrib import messages

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Inscription réussie ! Bienvenue.')
            return redirect('accueil')
    else:
        form = UserCreationForm()
    
    return render(request, 'utilisateurs/register.html', {'form': form})

def custom_logout(request):
    """Déconnexion immédiate par GET"""
    logout(request)
    messages.success(request, 'Vous avez été déconnecté avec succès.')
    return redirect('accueil')

