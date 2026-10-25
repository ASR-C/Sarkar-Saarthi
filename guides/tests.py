from datetime import timedelta
from django.core.exceptions import ValidationError
from django.test import TestCase, Client
from django.utils import timezone
from .models import Category, OfficialLink, Guide, GuideTranslation, validate_official_domain

class GuidesAndAllowlistTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.cat = Category.objects.create(name='Travel', slug='travel')
        self.valid_link = OfficialLink.objects.create(
            domain='passportindia.gov.in',
            url='https://passportindia.gov.in',
            label='Passport Seva'
        )

    def test_allowlist_accepts_valid_gov_domains(self):
        """Allowlist validator must accept legitimate .gov.in and .nic.in domains."""
        try:
            validate_official_domain('https://passportindia.gov.in/AppOnlineProject/welcomeLink')
            validate_official_domain('https://parivahan.gov.in/parivahan/')
            validate_official_domain('https://services.india.gov.in')
            validate_official_domain('https://scholarships.gov.in')
        except ValidationError:
            self.fail("validate_official_domain raised ValidationError unexpectedly on valid gov domain.")

    def test_allowlist_rejects_unauthorized_commercial_domains(self):
        """Allowlist validator must reject .com, .org, or phishing look-alikes."""
        with self.assertRaises(ValidationError):
            validate_official_domain('https://passport-online-agent.com')
        with self.assertRaises(ValidationError):
            validate_official_domain('https://aadhaar-update-scam.net')

    def test_outdated_guide_detection(self):
        """Guide verified over 30 days ago should flag is_outdated=True."""
        guide = Guide.objects.create(
            slug='test-guide',
            category=self.cat,
            official_link=self.valid_link,
            fee_text='₹100',
            last_verified_at=timezone.now() - timedelta(days=35)
        )
        self.assertTrue(guide.is_outdated)

        guide.last_verified_at = timezone.now() - timedelta(days=5)
        guide.save()
        self.assertFalse(guide.is_outdated)

    def test_guide_detail_view_renders_correctly(self):
        """Guide detail page must render the 10-point anatomy blocks."""
        guide = Guide.objects.create(
            slug='fresh-passport',
            category=self.cat,
            official_link=self.valid_link,
            fee_text='₹1,500',
            status='published',
            last_verified_at=timezone.now()
        )
        GuideTranslation.objects.create(
            guide=guide,
            language='en',
            title='Fresh Indian Passport',
            summary='How to apply for passport online.',
            common_mistakes='Wrong photo background.',
            what_to_do_if_fails='Call 1800-258-1800.'
        )

        response = self.client.get(f'/guides/{guide.slug}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Fresh Indian Passport')
        self.assertContains(response, '₹1,500')
        self.assertContains(response, 'https://passportindia.gov.in')
        self.assertContains(response, 'This is the official fee')

    def test_marwadi_translation_and_fallback(self):
        """Guide must serve Marwadi if present, or fallback to Hindi, then English."""
        guide = Guide.objects.create(
            slug='marwadi-test-guide',
            category=self.cat,
            official_link=self.valid_link,
            fee_text='Free',
            status='published'
        )
        t_en = GuideTranslation.objects.create(
            guide=guide,
            language='en',
            title='English Title',
            summary='English Summary'
        )
        t_hi = GuideTranslation.objects.create(
            guide=guide,
            language='hi',
            title='हिंदी शीर्षक',
            summary='हिंदी सारांश'
        )

        # Before Marwadi translation is added, requesting 'mwr' falls back to 'hi'
        trans = guide.get_translation('mwr')
        self.assertEqual(trans.language, 'hi')
        self.assertEqual(trans.title, 'हिंदी शीर्षक')

        # Add Marwadi translation
        t_mwr = GuideTranslation.objects.create(
            guide=guide,
            language='mwr',
            title='मारवाड़ी शीर्षक',
            summary='मारवाड़ी सारांश'
        )
        trans_mwr = guide.get_translation('mwr')
        self.assertEqual(trans_mwr.language, 'mwr')
        self.assertEqual(trans_mwr.title, 'मारवाड़ी शीर्षक')

