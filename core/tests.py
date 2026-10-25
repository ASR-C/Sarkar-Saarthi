from django.test import TestCase, Client

class LanguageAndCoreTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_set_language_to_marwadi(self):
        """Setting language to 'mwr' (Marwadi) should update session and redirect."""
        response = self.client.get('/set-language/?lang=mwr&next=/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/')
        self.assertEqual(self.client.session.get('lang'), 'mwr')

    def test_marwadi_homepage_context_and_switcher(self):
        """When language is Marwadi, page should render Marwadi labels and language switcher."""
        session = self.client.session
        session['lang'] = 'mwr'
        session.save()

        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        # Check language switcher items are rendered
        self.assertContains(response, 'मारवाड़ी')
        self.assertContains(response, 'हिन्दी')
        self.assertContains(response, 'EN')
        # Check Marwadi nav labels
        self.assertContains(response, 'सगळी गाइड्स')
        self.assertContains(response, 'सरकारी वेबसाइट्स')
