from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.urls import reverse
from .models import Event, Artist, Composition, Like
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q


def home(request):
    # Get featured events (or notable past events if no featured ones)
    featured_events = Event.objects.filter(is_featured=True).order_by('-date')[:3]
    
    # If there are not enough featured events, supplement with regular past events
    if featured_events.count() < 3:
        additional_events = Event.objects.all().exclude(
            id__in=featured_events.values_list('id', flat=True)
        ).order_by('-date')[:3-featured_events.count()]
        
        featured_events = list(featured_events) + list(additional_events)
    
    # Get past events for the events section
    past_events = Event.objects.all().order_by('-date')[:3]
    all_events = Event.objects.all().order_by('-date')
    # Get featured artists (or artists with most likes if no featured ones)
    featured_artists = list(Artist.objects.filter(is_featured=True)[:4])
    
    # If there are not enough featured artists, supplement with popular artists
    if len(featured_artists) < 4:
        # Use a raw query to get artists with the most likes
        from django.db.models import Count
        popular_artists = Artist.objects.annotate(
            like_count=Count('likes')
        ).exclude(
            id__in=[artist.id for artist in featured_artists]
        ).order_by('-like_count')[:4-len(featured_artists)]
        
        featured_artists = featured_artists + list(popular_artists)
    
    # Get latest music compositions
    latest_music = Composition.objects.filter(type='music').order_by('-created_at')[:4]
    
    # Get latest video compositions
    latest_videos = Composition.objects.filter(type='video').order_by('-created_at')[:4]
    
    return render(request, 'events/home.html', {
        'featured_events': featured_events,
        'past_events': past_events,
        'featured_artists': featured_artists,
        'latest_music': latest_music,
        'latest_videos': latest_videos,
        'all_events': all_events,
    })


def event_list(request):
    # Get search query from URL parameter
    search_query = request.GET.get('search', '')
    
    # Filter events based on search query
    if search_query:
        events = Event.objects.filter(
            Q(title__icontains=search_query) | 
            Q(description__icontains=search_query) |
            Q(location__icontains=search_query)
        ).filter(date__lt=timezone.now()).order_by('-date')
    else:
        events = Event.objects.all().order_by('-date')
    
    # Set up pagination - 9 events per page
    paginator = Paginator(events, 9)
    page = request.GET.get('page')
    
    try:
        events_paginated = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page
        events_paginated = paginator.page(1)
    except EmptyPage:
        # If page is out of range, deliver last page of results
        events_paginated = paginator.page(paginator.num_pages)
    
    return render(request, 'events/event_list.html', {
        'events': events_paginated,
        'search_query': search_query,
    })


def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    events = Event.objects.all().exclude(id=event_id).order_by('-date')[:3]
    return render(request, 'events/event_detail.html', {
        'event': event,
        'events': events,
    })


def artist_list(request):
    # Get search query from URL parameter
    search_query = request.GET.get('search', '')
    
    # Filter artists based on search query
    if search_query:
        artists = Artist.objects.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        ).order_by('name')
    else:
        artists = Artist.objects.all().order_by('name')
    
    # Set up pagination - 12 artists per page
    paginator = Paginator(artists, 12)
    page = request.GET.get('page')
    
    try:
        artists_paginated = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page
        artists_paginated = paginator.page(1)
    except EmptyPage:
        # If page is out of range, deliver last page of results
        artists_paginated = paginator.page(paginator.num_pages)
    
    return render(request, 'events/artist_list.html', {
        'artists': artists_paginated,
        'search_query': search_query,
    })


def artist_detail(request, artist_id):
    artist = get_object_or_404(Artist, id=artist_id)
    
    # Get user or session-based likes
    is_liked = False
    if request.user.is_authenticated:
        is_liked = Like.objects.filter(user=request.user, artist=artist).exists()
    elif 'sessionid' in request.COOKIES:
        session_key = request.COOKIES.get('sessionid')
        is_liked = Like.objects.filter(session_key=session_key, artist=artist).exists()
    
    # Separate compositions by type
    music = artist.compositions.filter(type='music').order_by('-created_at')
    videos = artist.compositions.filter(type='video').order_by('-created_at')
    
    return render(request, 'events/artist_detail.html', {
        'artist': artist,
        'music': music,
        'videos': videos,
        'is_liked': is_liked,
        'now': timezone.now(),
    })


@require_POST
def toggle_like(request):
    """Toggle like for an artist"""
    artist_id = request.POST.get('artist_id')
    
    if not artist_id:
        return JsonResponse({'error': 'Missing artist ID'}, status=400)
    
    artist = get_object_or_404(Artist, id=artist_id)
    
    # Find or create the like
    if request.user.is_authenticated:
        # For logged-in users
        like, created = Like.objects.get_or_create(
            user=request.user,
            artist=artist
        )
        
        if not created:
            # If the like already existed, remove it (unlike)
            like.delete()
            action = 'unliked'
        else:
            action = 'liked'
    else:
        # For anonymous users
        session_key = request.COOKIES.get('sessionid')
        if not session_key:
            # Create a session if one doesn't exist
            request.session.save()
            session_key = request.session.session_key
        
        like, created = Like.objects.get_or_create(
            session_key=session_key,
            artist=artist
        )
        
        if not created:
            # If the like already existed, remove it (unlike)
            like.delete()
            action = 'unliked'
        else:
            action = 'liked'
    
    # Count the new like total
    like_count = Like.objects.filter(artist=artist).count()
    
    # If it's an AJAX request, return JSON, otherwise redirect back
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'action': action,
            'like_count': like_count,
        })
    else:
        return HttpResponseRedirect(reverse('artist_detail', args=[artist.id]))


def composition_detail(request, composition_id):
    composition = get_object_or_404(Composition, id=composition_id)
    
    return render(request, 'events/composition_detail.html', {
        'composition': composition,
    })

def media_list(request):
    """View for showing all compositions (both music and videos)"""
    # Get search query from URL parameter
    search_query = request.GET.get('search', '')
    
    # Filter compositions based on search query
    if search_query:
        compositions = Composition.objects.filter(
            Q(title__icontains=search_query) | 
            Q(description__icontains=search_query) |
            Q(artist__name__icontains=search_query)
        ).order_by('-created_at')
    else:
        compositions = Composition.objects.all().order_by('-created_at')
    
    # Set up pagination - 12 compositions per page
    paginator = Paginator(compositions, 12)
    page = request.GET.get('page')
    
    try:
        compositions_paginated = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page
        compositions_paginated = paginator.page(1)
    except EmptyPage:
        # If page is out of range, deliver last page of results
        compositions_paginated = paginator.page(paginator.num_pages)
    
    return render(request, 'events/media_list.html', {
        'compositions': compositions_paginated,
        'search_query': search_query,
    })

def all_music(request):
    """View for showing all music compositions"""
    # Get all music compositions without pagination or search filtering
    all_music = Composition.objects.filter(type='music').order_by('-created_at')
    
    return render(request, 'events/all_music.html', {
        'music': all_music,
        'all_music': all_music,
    })

def all_videos(request):
    """View for showing all video compositions"""
    # Get all video compositions without pagination or search filtering
    videos = Composition.objects.filter(type='video').order_by('-created_at')
    
    return render(request, 'events/all_videos.html', {
        'videos': videos,
    }) 