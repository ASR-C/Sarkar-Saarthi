from django.contrib import admin
from .models import WizardQuestion

@admin.register(WizardQuestion)
class WizardQuestionAdmin(admin.ModelAdmin):
    list_display = ('question_key', 'position', 'category', 'text_en', 'yes_outcome_guide', 'no_outcome_guide')
    list_filter = ('category',)
    search_fields = ('question_key', 'text_en', 'text_hi')
