from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Event, Artist, Composition


class EventSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Event.objects.all()

    def lastmod(self, obj):
        return obj.updated_at if hasattr(obj, 'updated_at') else None

    def location(self, obj):
        return reverse('event_detail', args=[obj.slug])


class ArtistSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return Artist.objects.all()

    def lastmod(self, obj):
        return obj.updated_at if hasattr(obj, 'updated_at') else None

    def location(self, obj):
        return reverse('artist_detail', args=[obj.slug])


class CompositionSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.6

    def items(self):
        return Composition.objects.all()

    def lastmod(self, obj):
        return obj.created_at

    def location(self, obj):
        return reverse('composition_detail', args=[obj.slug])


class StaticSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        return ['home', 'event_list', 'artist_list', 'all_music', 'all_videos', 'contact']

    def location(self, item):
        return reverse(item) 