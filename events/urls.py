from django.urls import path
from . import views

urlpatterns = [
    # Home page
    path('', views.home, name='home'),
    
    # Event URLs
    path('events/', views.event_list, name='event_list'),
    path('events/<int:event_id>/', views.event_detail, name='event_detail'),
    
    # Artist URLs
    path('artists/', views.artist_list, name='artist_list'),
    path('artists/<int:artist_id>/', views.artist_detail, name='artist_detail'),
    
    # Composition URL
    path('compositions/<int:composition_id>/', views.composition_detail, name='composition_detail'),
    
    # Like functionality
    path('like/', views.toggle_like, name='toggle_like'),
] 