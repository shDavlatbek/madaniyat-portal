from django.contrib import admin
from .models import Event, Artist, Composition, Like, SiteSettings, Murojat


class CompositionInline(admin.StackedInline):
    model = Composition
    extra = 0


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
    list_display = ('title', 'date', 'location', 'is_featured', 'has_ticket_price', 'artists_count')
    list_filter = ('date', 'is_featured')
    search_fields = ('title', 'description', 'location')
    filter_horizontal = ('artists',)
    list_editable = ('is_featured',)
    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('title', 'slug', 'description', 'date', 'location', 'type', 'is_featured', 'image')
        }),
        ('Xarita ma\'lumotlari', {
            'fields': ('latitude', 'longitude'),
            'classes': ('collapse',),
        }),
        ('Bilet ma\'lumotlari', {
            'fields': ('ticket_price', 'ticket_url'),
        }),
        ('Ishtirokchilar', {
            'fields': ('artists',),
        }),
    )
    
    def artists_count(self, obj):
        return obj.artists.count()
    artists_count.short_description = "Artists"
    
    def has_ticket_price(self, obj):
        if obj.ticket_price and obj.ticket_price > 0:
            return f"✓ {obj.ticket_price} so'm"
        return "✗ Tekin"
    has_ticket_price.short_description = "Bilet narxi"


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


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('site_name', 'contact_email', 'contact_phone', 'contact_address')
        }),
        ('Ijtimoiy tarmoqlar', {
            'fields': ('facebook_url', 'instagram_url', 'youtube_url', 'twitter_url', 'telegram_url')
        }),
        ('Aloqa sahifasi', {
            'fields': ('contact_page_title', 'contact_page_description', 'google_maps_embed')
        }),
        ('Footer', {
            'fields': ('footer_text',)
        }),
    )
    
    def has_add_permission(self, request):
        # Check if a SiteSettings object already exists
        if SiteSettings.objects.exists():
            return False
        return super().has_add_permission(request)
    
    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of the settings object
        return False


@admin.register(Murojat)
class MurojatAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'subject', 'created_at', 'status')
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'phone', 'message')
    readonly_fields = ('name', 'phone', 'subject', 'message', 'created_at')
    fieldsets = (
        ('Murojat ma\'lumotlari', {
            'fields': ('name', 'phone', 'subject', 'message', 'created_at')
        }),
        ('Holati', {
            'fields': ('status', 'notes')
        }),
    )
    list_editable = ('status',)
    date_hierarchy = 'created_at'
    
    def has_add_permission(self, request):
        # Prevent adding contacts directly through admin
        return False
    
    def has_delete_permission(self, request, obj=None):
        # Allow deletion for superusers only
        return request.user.is_superuser 