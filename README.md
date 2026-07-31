# Gestion de Bibliotheque

Application web de gestion d'une bibliotheque developpee avec Django. Elle permet de gerer un catalogue d'ouvrages, les emprunts et les utilisateurs, avec un systeme de notifications automatiques.

## Fonctionnalites

- Catalogue des ressources (livres, films)
- Gestion des emprunts et des locations
- Gestion des utilisateurs et de leurs comptes
- Systeme de notifications automatiques
- Paiement simule pour les locations
- Interface d'administration Django

## Stack technique

- Python / Django
- SQLite (base de donnees)
- HTML / CSS (templates Django)

## Architecture

Le projet est organise en applications Django :

- `bibliotheque` : gestion du catalogue, des emprunts et des locations
- `notifications` : envoi et suivi des notifications
- `utilisateurs` : gestion des comptes et de l'authentification

## Installation

```bash
git clone https://github.com/narjessmhibik/webdj2ba.git
cd webdj2ba/webproject/gestion_bibliotheque
python -m venv venv
source venv/bin/activate        # sous Windows : venv\Scripts\activate
pip install django
python manage.py migrate
python manage.py runserver
```

L'application est ensuite accessible sur http://127.0.0.1:8000/

## Auteur

Narjess Mhibik
