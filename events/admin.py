from django.contrib import admin
from .models import Event, Artist, Composition, Like


class CompositionInline(admin.TabularInline):
    model = Composition
    extra = 1


@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_featured', 'compositions_count', 'likes_count', 'created_at')
    list_filter = ('is_featured',)
    search_fields = ('name',)
    inlines = [CompositionInline]
    list_editable = ('is_featured',)
    
    def compositions_count(self, obj):
        return obj.compositions.count()
    compositions_count.short_description = "Compositions"
    
    def likes_count(self, obj):
        return obj.likes.count()
    likes_count.short_description = "Likes"


@admin.register(Composition)
class CompositionAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'type', 'created_at')
    list_filter = ('type', 'artist')
    search_fields = ('title', 'artist__name')


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'location', 'is_featured', 'artists_count')
    list_filter = ('date', 'is_featured')
    search_fields = ('title', 'description', 'location')
    filter_horizontal = ('artists',)
    list_editable = ('is_featured',)
    
    def artists_count(self, obj):
        return obj.artists.count()
    artists_count.short_description = "Artists"


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('get_artist', 'get_source', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('artist__name', 'user__username')
    
    def get_artist(self, obj):
        return obj.artist.name
    get_artist.short_description = "Artist"
    
    def get_source(self, obj):
        return obj.user.username if obj.user else f"Anonymous ({obj.session_key})"
    get_source.short_description = "Liked by" 