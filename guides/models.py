from datetime import timedelta
from urllib.parse import urlparse
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


def validate_official_domain(url: str):
    """
    Validates that outbound link belongs to approved official domains.
    Must be .gov.in, .nic.in, or verified educational portals like .res.in / nta.ac.in.
    """
    parsed = urlparse(url)
    domain = (parsed.hostname or '').lower()
    allowed_endings = ('.gov.in', '.nic.in', '.ac.in', '.res.in', 'digilocker.gov.in', 'parivahan.gov.in')
    if not any(domain.endswith(ending) or domain == ending for ending in allowed_endings):
        raise ValidationError(
            f"Domain '{domain}' is not on the official government allowlist (.gov.in, .nic.in, etc.)."
        )


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, max_length=100)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children')
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'categories'
        ordering = ['sort_order', 'name']
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class OfficialLink(models.Model):
    domain = models.CharField(max_length=150, help_text="e.g. passportindia.gov.in")
    url = models.URLField(max_length=500, validators=[validate_official_domain])
    label = models.CharField(max_length=200)
    state_scope = models.CharField(max_length=50, default='central', help_text="'central' or state name")
    verified_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'official_links'
        ordering = ['label']
        verbose_name = 'Official Link'
        verbose_name_plural = 'Official Links Allowlist'

    def __str__(self):
        return f"{self.label} ({self.domain})"

    def clean(self):
        parsed = urlparse(self.url)
        self.domain = (parsed.hostname or '').lower()
        validate_official_domain(self.url)


class Guide(models.Model):
    MODE_CHOICES = (
        ('online', 'Fully Online'),
        ('partial', 'Partly Online (Visit Needed)'),
        ('in_person', 'In-Person Only'),
    )
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('needs_review', 'Needs Review'),
        ('published', 'Published'),
    )

    slug = models.SlugField(unique=True, max_length=150)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='guides')
    state_scope = models.CharField(max_length=50, default='central', help_text="'central' or state name")
    mode = models.CharField(max_length=20, choices=MODE_CHOICES, default='online')
    fee_text = models.CharField(max_length=150, help_text="e.g. '₹1,500' or 'Free / ₹0'")
    last_date = models.CharField(max_length=100, blank=True, help_text="Deadline or 'Rolling'")
    official_link = models.ForeignKey(OfficialLink, on_delete=models.PROTECT, related_name='guides')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='published')
    last_verified_at = models.DateTimeField(default=timezone.now)
    verified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'guides'
        ordering = ['-last_verified_at']
        verbose_name = 'Guide'
        verbose_name_plural = 'Guides'

    def __str__(self):
        trans = self.translations.filter(language='en').first()
        return trans.title if trans else self.slug

    @property
    def is_outdated(self) -> bool:
        """Older than 30 days shows a visible 'may be outdated, check the official site' banner."""
        if not self.last_verified_at:
            return True
        return timezone.now() - self.last_verified_at > timedelta(days=30)

    def get_translation(self, lang='en'):
        trans = self.translations.filter(language=lang).first()
        if not trans and lang == 'mwr':
            trans = self.translations.filter(language='hi').first()
        if not trans and lang != 'en':
            trans = self.translations.filter(language='en').first()
        return trans

    def get_steps(self, lang='en'):
        steps = self.steps.filter(language=lang).order_by('position')
        if not steps.exists() and lang == 'mwr':
            steps = self.steps.filter(language='hi').order_by('position')
        if not steps.exists() and lang != 'en':
            steps = self.steps.filter(language='en').order_by('position')
        return steps


class GuideTranslation(models.Model):
    LANGUAGE_CHOICES = (
        ('en', 'English'),
        ('hi', 'हिन्दी (Hindi)'),
        ('mwr', 'मारवाड़ी (Marwadi)'),
    )

    guide = models.ForeignKey(Guide, on_delete=models.CASCADE, related_name='translations')
    language = models.CharField(max_length=10, choices=LANGUAGE_CHOICES, default='en')
    title = models.CharField(max_length=255)
    summary = models.TextField(help_text="One-line summary for citizens")
    common_mistakes = models.TextField(help_text="Common mistakes that cause rejection (bullet points)")
    what_to_do_if_fails = models.TextField(help_text="Helpline, grievance portal, re-apply rules")
    machine_translated = models.BooleanField(default=False)
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = 'guide_translations'
        unique_together = ('guide', 'language')
        verbose_name = 'Guide Translation'
        verbose_name_plural = 'Guide Translations'

    def __str__(self):
        return f"{self.title} [{self.language}]"


class GuideStep(models.Model):
    guide = models.ForeignKey(Guide, on_delete=models.CASCADE, related_name='steps')
    position = models.PositiveIntegerField(default=1)
    language = models.CharField(max_length=10, default='en')
    body = models.TextField(help_text="Plain-language explanation of this step")
    portal_label_en = models.CharField(max_length=150, blank=True, help_text="e.g. Click 'Apply for Fresh Passport'")

    class Meta:
        db_table = 'guide_steps'
        ordering = ['position']
        verbose_name = 'Guide Step'
        verbose_name_plural = 'Guide Steps'

    def __str__(self):
        return f"Step {self.position} - {self.guide.slug} ({self.language})"


class GuideDocument(models.Model):
    KIND_CHOICES = (
        ('photo', 'Photo'),
        ('signature', 'Signature'),
        ('id', 'ID Proof'),
        ('address', 'Address Proof'),
        ('other', 'Other Document'),
    )

    guide = models.ForeignKey(Guide, on_delete=models.CASCADE, related_name='documents')
    name = models.CharField(max_length=150)
    kind = models.CharField(max_length=20, choices=KIND_CHOICES, default='other')
    allowed_formats = models.CharField(max_length=100, default='JPEG, JPG, PDF')
    min_kb = models.PositiveIntegerField(null=True, blank=True)
    max_kb = models.PositiveIntegerField(null=True, blank=True)
    width_px = models.PositiveIntegerField(null=True, blank=True)
    height_px = models.PositiveIntegerField(null=True, blank=True)
    dpi = models.PositiveIntegerField(null=True, blank=True)
    notes = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = 'guide_documents'
        verbose_name = 'Guide Document Spec'
        verbose_name_plural = 'Guide Document Specs'

    def __str__(self):
        return f"{self.name} for {self.guide.slug}"
