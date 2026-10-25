from django.contrib import admin
from .models import Category, OfficialLink, Guide, GuideTranslation, GuideStep, GuideDocument

class GuideTranslationInline(admin.StackedInline):
    model = GuideTranslation
    extra = 1

class GuideStepInline(admin.TabularInline):
    model = GuideStep
    extra = 2
    fields = ('position', 'language', 'body', 'portal_label_en')

class GuideDocumentInline(admin.TabularInline):
    model = GuideDocument
    extra = 1

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'parent', 'sort_order')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(OfficialLink)
class OfficialLinkAdmin(admin.ModelAdmin):
    list_display = ('label', 'domain', 'url', 'state_scope', 'verified_at', 'is_active')
    list_filter = ('is_active', 'state_scope')
    search_fields = ('label', 'domain', 'url')

@admin.register(Guide)
class GuideAdmin(admin.ModelAdmin):
    list_display = ('slug', 'category', 'mode', 'fee_text', 'status', 'last_verified_at')
    list_filter = ('status', 'mode', 'category', 'state_scope')
    search_fields = ('slug', 'translations__title')
    inlines = [GuideTranslationInline, GuideStepInline, GuideDocumentInline]
