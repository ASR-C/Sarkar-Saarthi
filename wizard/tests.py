from django.test import TestCase, Client
from guides.models import Category, OfficialLink, Guide
from .models import WizardQuestion

class WizardTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.cat = Category.objects.create(name='Travel', slug='travel')
        self.link = OfficialLink.objects.create(domain='passportindia.gov.in', url='https://passportindia.gov.in', label='Passport')
        self.guide = Guide.objects.create(
            slug='passport-guide',
            category=self.cat,
            official_link=self.link,
            fee_text='₹1,500',
            status='published'
        )
        self.q1 = WizardQuestion.objects.create(
            question_key='q1_travel',
            category=self.cat,
            position=1,
            text_en='Do you need a passport?',
            yes_outcome_guide=self.guide
        )

    def test_wizard_start_session_initialization(self):
        """Starting wizard sets up session and forwards to first question."""
        response = self.client.post('/wizard/', {
            'category_id': self.cat.id,
            'state': 'Central / All India'
        })
        self.assertEqual(response.status_code, 302)
        self.assertIn(f'/wizard/step/{self.q1.id}/', response.url)

    def test_wizard_yes_outcome_leads_to_result(self):
        """Answering Yes to question with outcome guide redirects to result page."""
        response = self.client.post(f'/wizard/step/{self.q1.id}/', {'answer': 'yes'})
        self.assertEqual(response.status_code, 302)
        self.assertIn(f'/wizard/result/{self.guide.slug}/', response.url)

    def test_wizard_step_marwadi_question_rendering(self):
        """Wizard question should render text_mwr when language is Marwadi."""
        self.q1.text_mwr = 'कांईं थारे पासपोर्ट री जरूरत है?'
        self.q1.save()

        session = self.client.session
        session['lang'] = 'mwr'
        session['wizard_category_id'] = self.cat.id
        session['wizard_answers'] = []
        session.save()

        response = self.client.get(f'/wizard/step/{self.q1.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'कांईं थारे पासपोर्ट री जरूरत है?')

