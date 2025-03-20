from django.db import models
from django.contrib.auth.models import User
from tinymce.models import HTMLField
from django.utils.text import slugify


class Artist(models.Model):
    name = models.CharField(max_length=255, verbose_name="Sanʼatkor nomi")
    slug = models.SlugField(max_length=255, unique=True, blank=True, verbose_name="URL slug")
    description = HTMLField(verbose_name="Sanʼatkor tafsilotlari")
    image = models.ImageField(upload_to='artists/', null=True, blank=True, verbose_name="Sanʼatkor rasmi")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan vaqt")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="O'zgartirilgan vaqt")
    is_featured = models.BooleanField(default=False)
    facebook_url = models.URLField(blank=True, null=True, verbose_name="Facebook URL")
    instagram_url = models.URLField(blank=True, null=True, verbose_name="Instagram URL")
    youtube_url = models.URLField(blank=True, null=True, verbose_name="YouTube URL")
    x_url = models.URLField(blank=True, null=True, verbose_name="X URL")
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            # Ensure slug is unique
            original_slug = self.slug
            count = 1
            while Artist.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{count}"
                count += 1
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Sanʼatkor "
        verbose_name_plural = "Sanʼatkorlar"


class CompositionType(models.TextChoices):
    MUSIC = 'music', 'Music'
    VIDEO = 'video', 'Video'


EVENT_TYPE = [
    ('local', 'Mahalliy'),
    ('international', 'Xorijiy'),
]


class Composition(models.Model):
    cover_image = models.ImageField(upload_to='composition_covers/', blank=True, null=True, verbose_name="Kompozitsiya rasmi")
    title = models.CharField(max_length=255, verbose_name="Kompozitsiya nomi")
    slug = models.SlugField(max_length=255, unique=True, blank=True, verbose_name="URL slug")
    description = models.TextField(blank=True, null=True, verbose_name="Kompozitsiya tafsilotlari")
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='compositions', verbose_name="Sanʼatkor")
    type = models.CharField(max_length=10, choices=CompositionType.choices, default=CompositionType.MUSIC, verbose_name="Turi")
    file = models.FileField(upload_to='compositions/', null=True, blank=True, verbose_name="Fayl")
    link = models.URLField(blank=True, null=True, verbose_name="Youtube havola")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan vaqt")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="O'zgartirilgan vaqt")
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            # Add artist name to slug for uniqueness
            self.slug = f"{base_slug}-{slugify(self.artist.name)}"
            # Ensure slug is unique
            original_slug = self.slug
            count = 1
            while Composition.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{count}"
                count += 1
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.title} - {self.artist.name}"
    
    class Meta:
        verbose_name = "Kompozitsiya "
        verbose_name_plural = "Kompozitsiyalar"


class Event(models.Model):
    image = models.ImageField(upload_to='events/', null=True, blank=True, verbose_name="Tadbir rasm")
    title = models.CharField(max_length=255, verbose_name="Tadbir nomi")
    slug = models.SlugField(max_length=255, unique=True, blank=True, verbose_name="URL slug")
    description = HTMLField(verbose_name="Tadbir tafsilotlari")
    date = models.DateTimeField(verbose_name="Tadbir sanasi")
    location = models.CharField(max_length=255, verbose_name="Tadbir manzili")
    type = models.CharField(max_length=255, choices=EVENT_TYPE, verbose_name="Tadbir turi")
    artists = models.ManyToManyField(Artist, related_name='events', blank=True, verbose_name="Sanʼatkorlar")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan vaqt")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="O'zgartirilgan vaqt")
    is_featured = models.BooleanField(default=False)
    latitude = models.FloatField(blank=True, null=True, verbose_name="Xaritada kenglik")
    longitude = models.FloatField(blank=True, null=True, verbose_name="Xaritada uzunlik")
    ticket_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Bilet narxi")
    ticket_url = models.URLField(blank=True, null=True, verbose_name="Bilet sotib olish havolasi")
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            # Ensure slug is unique
            original_slug = self.slug
            count = 1
            while Event.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{count}"
                count += 1
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = "Tadbir "
        verbose_name_plural = "Tadbirlar"
        ordering = ['-date']


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Foydalanuvchi")
    session_key = models.CharField(max_length=40, null=True, blank=True, verbose_name="Session key")
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='likes', verbose_name="Sanʼatkor")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan vaqt")
    
    class Meta:
        verbose_name = "Like "
        verbose_name_plural = "Like lar"
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'artist'],
                condition=models.Q(user__isnull=False),
                name='unique_user_artist_like'
            ),
            models.UniqueConstraint(
                fields=['session_key', 'artist'],
                condition=models.Q(session_key__isnull=False),
                name='unique_session_artist_like'
            ),
        ]
    
    def __str__(self):
        source = self.user.username if self.user else "Anonymous"
        return f"{source} likes {self.artist.name}"


class SiteSettings(models.Model):
    """Model to store site-wide settings including contact and footer information"""
    site_name = models.CharField(max_length=255, default="Madaniyat Vazirligi", verbose_name="Sayt nomi")
    contact_email = models.EmailField(verbose_name="Aloqa email", default="info@madaniyat.uz")
    contact_phone = models.CharField(max_length=100, verbose_name="Telefon raqam", default="+998 71 123 4567")
    contact_address = models.TextField(verbose_name="Manzil", default="100128, Toshkent, Oʻzbekiston")
    
    # Social media links
    facebook_url = models.URLField(blank=True, null=True, verbose_name="Facebook URL")
    instagram_url = models.URLField(blank=True, null=True, verbose_name="Instagram URL")
    youtube_url = models.URLField(blank=True, null=True, verbose_name="YouTube URL")
    twitter_url = models.URLField(blank=True, null=True, verbose_name="Twitter URL")
    telegram_url = models.URLField(blank=True, null=True, verbose_name="Telegram URL")
    
    # Contact page content
    contact_page_title = models.CharField(max_length=255, default="Biz bilan bog'lanish", verbose_name="Aloqa sahifa sarlavhasi")
    contact_page_description = HTMLField(verbose_name="Aloqa sahifa mazmuni", blank=True)
    google_maps_embed = models.TextField(verbose_name="Google Maps iframe kodi", blank=True, help_text="Google Maps-dan olingan joylashuv HTML kodi")
    
    # Additional footer information
    footer_text = models.TextField(blank=True, verbose_name="Footer qo'shimcha matn")
    
    class Meta:
        verbose_name = "Sayt sozlamalari"
        verbose_name_plural = "Sayt sozlamalari"
    
    def __str__(self):
        return "Sayt sozlamalari"
    
    @classmethod
    def get_settings(cls):
        """Returns the site settings, creating a default instance if none exists"""
        settings, created = cls.objects.get_or_create(pk=1)
        return settings


class Murojat(models.Model):
    """Model to store contact form submissions"""
    STATUS_CHOICES = [
        ('new', 'Yangi'),
        ('processing', 'Ko\'rib chiqilmoqda'),
        ('completed', 'Bajarildi'),
        ('rejected', 'Rad etildi'),
    ]
    
    name = models.CharField(max_length=255, verbose_name="F.I.Sh")
    phone = models.CharField(max_length=20, verbose_name="Telefon raqami")
    subject = models.CharField(max_length=255, blank=True, null=True, verbose_name="Mavzu")
    message = models.TextField(verbose_name="Xabar")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yuborilgan vaqt")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name="Holati")
    notes = models.TextField(blank=True, null=True, verbose_name="Admin izohlari")
    
    class Meta:
        verbose_name = "Murojat"
        verbose_name_plural = "Murojatlar"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.created_at.strftime('%d.%m.%Y %H:%M')}" 