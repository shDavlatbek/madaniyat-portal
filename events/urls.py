from django.urls import path
from . import views
from django.views.generic import RedirectView

urlpatterns = [
    # Home page
    path('', views.home, name='home'),
    
    # Event URLs
    path('events/', views.event_list, name='event_list'),
    path('events/<int:event_id>/', views.event_detail, name='event_detail'),
    
    # Artist URLs
    path('artists/', views.artist_list, name='artist_list'),
    path('artists/<int:artist_id>/', views.artist_detail, name='artist_detail'),
    
    # Media URLs - redirect media_list to all_music
    path('medias/', RedirectView.as_view(pattern_name='all_music'), name='media_list'),
    path('medias/music/', views.all_music, name='all_music'),
    path('medias/videos/', views.all_videos, name='all_videos'),
    
    # Composition URL
    path('compositions/<int:composition_id>/', views.composition_detail, name='composition_detail'),
    
    # Like functionality
    path('like/', views.toggle_like, name='toggle_like'),
] 