# bibliotheque/forms.py
from django import forms
from .models import Avis

class AvisForm(forms.ModelForm):
    class Meta:
        model = Avis
        fields = ['note', 'commentaire']
        widgets = {
            'commentaire': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Partagez votre avis sur ce film...'
            }),
            'note': forms.Select(attrs={'class': 'form-select'}, choices=[
                ('', 'Choisissez une note'),
                (1, '★ - Décevant'),
                (2, '★★ - Moyen'),
                (3, '★★★ - Bon'),
                (4, '★★★★ - Très bon'),
                (5, '★★★★★ - Excellent')
            ])
        }
        labels = {
            'commentaire': 'Votre commentaire (optionnel)',
            'note': 'Note'
        }

class FormulairePaiementSimule(forms.Form):
    """Formulaire de simulation de paiement académique"""
    
    METHODES = [
        ('carte', '💳 Carte bancaire'),
        ('paypal', '🔵 PayPal'),
        ('crypto', '₿ Cryptomonnaie'),
    ]
    
    methode = forms.ChoiceField(
        choices=METHODES,
        label="Méthode de paiement",
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )
    
    # Champs fictifs pour carte bancaire
    numero_carte = forms.CharField(
        max_length=19,
        required=False,
        label="Numéro de carte",
        widget=forms.TextInput(attrs={
            'placeholder': '4242 4242 4242 4242',
            'class': 'form-control'
        })
    )
    
    date_expiration = forms.CharField(
        max_length=7,
        required=False,
        label="Date d'expiration (MM/AAAA)",
        widget=forms.TextInput(attrs={
            'placeholder': '12/2025',
            'class': 'form-control'
        })
    )
    
    cvv = forms.CharField(
        max_length=4,
        required=False,
        label="CVV",
        widget=forms.PasswordInput(attrs={
            'placeholder': '123',
            'class': 'form-control'
        })
    )
    
    # Champs pour accepter les conditions
    conditions = forms.BooleanField(
        required=True,
        label="J'accepte que ce paiement soit une simulation (aucun argent réel ne sera débité)",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    def clean(self):
        """Validation pour la simulation"""
        cleaned_data = super().clean()
        methode = cleaned_data.get('methode')
        
        # Pour la simulation, on accepte n'importe quelle valeur
        # Mais on peut ajouter des vérifications basiques pour l'UX
        if methode == 'carte':
            numero = cleaned_data.get('numero_carte', '').replace(' ', '')
            if not numero:
                # Pour la simulation, on suggère juste
                self.add_error('numero_carte', 
                    'Pour la simulation, vous pouvez utiliser: 4242 4242 4242 4242')
            elif len(numero) != 16 or not numero.isdigit():
                # On accepte quand même pour la simulation
                pass
        
        return cleaned_data