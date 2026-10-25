from django.db import models
from guides.models import Category, Guide

class WizardQuestion(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True, related_name='wizard_questions')
    position = models.PositiveIntegerField(default=1)
    question_key = models.CharField(max_length=100, unique=True, help_text="e.g. passport_first_time, dl_learner_held")
    text_en = models.CharField(max_length=255, help_text="e.g. Are you applying for a passport for the first time?")
    text_hi = models.CharField(max_length=255, help_text="हिन्दी प्रश्न")
    text_mwr = models.CharField(max_length=255, blank=True, default='', help_text="मारवाड़ी प्रश्न")
    
    yes_next = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='yes_predecessors')
    no_next = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='no_predecessors')
    
    yes_outcome_guide = models.ForeignKey(Guide, on_delete=models.SET_NULL, null=True, blank=True, related_name='yes_wizard_outcomes')
    no_outcome_guide = models.ForeignKey(Guide, on_delete=models.SET_NULL, null=True, blank=True, related_name='no_wizard_outcomes')

    class Meta:
        db_table = 'wizard_questions'
        ordering = ['position']
        verbose_name = 'Wizard Question'
        verbose_name_plural = 'Wizard Questions'

    def __str__(self):
        return f"Q{self.position}: {self.question_key}"
