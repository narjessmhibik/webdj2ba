from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from utilisateurs import views as utilisateurs_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('bibliotheque.urls')),
    path('utilisateurs/', include('utilisateurs.urls')),
    path('notifications/', include('notifications.urls')),
    
    path('login/', auth_views.LoginView.as_view(
        template_name='utilisateurs/login.html',
        next_page='accueil'
    ), name='login'),
    
    path('logout/', auth_views.LogoutView.as_view(next_page='accueil'), name='logout'),
    
    path('register/', utilisateurs_views.register, name='register'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)