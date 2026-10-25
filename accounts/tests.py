from datetime import timedelta
from django.test import TestCase, Client
from django.utils import timezone
from .models import User, SignupOTP

class AccountsAndOTPTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='citizen@example.com',
            password='SafePassword123!',
            name='Ramesh Sharma',
            language='en',
            state='Rajasthan'
        )

    def test_user_creation_unverified_by_default(self):
        """User status must be 'unverified' by default until OTP is confirmed."""
        self.assertEqual(self.user.status, 'unverified')
        self.assertFalse(self.user.is_staff)

    def test_otp_hash_storage_not_plain_text(self):
        """OTP must never be stored as plain text, only as an HMAC hash."""
        plain_otp = SignupOTP.create_for_user(self.user)
        otp_record = SignupOTP.objects.filter(user=self.user).first()
        self.assertIsNotNone(otp_record)
        self.assertNotEqual(otp_record.otp_hash, plain_otp)
        self.assertEqual(len(otp_record.otp_hash), 64) # SHA256 hex string

    def test_otp_verification_success_activates_user(self):
        """Entering correct OTP within 10 minutes activates user account."""
        plain_otp = SignupOTP.create_for_user(self.user)
        success, msg = SignupOTP.verify(self.user, plain_otp)
        self.assertTrue(success)
        self.user.refresh_from_db()
        self.assertEqual(self.user.status, 'active')

    def test_otp_wrong_attempts_limit_and_invalidation(self):
        """5 incorrect attempts must invalidate the OTP."""
        plain_otp = SignupOTP.create_for_user(self.user)
        for i in range(1, 5):
            success, msg = SignupOTP.verify(self.user, '000000')
            self.assertFalse(success)
            self.assertIn(f"{5 - i} attempt(s) remaining", msg)

        # 5th failed attempt invalidates
        success, msg = SignupOTP.verify(self.user, '000000')
        self.assertFalse(success)
        self.assertIn("Maximum attempts reached", msg)

        # Even correct OTP now fails
        success, msg = SignupOTP.verify(self.user, plain_otp)
        self.assertFalse(success)
        self.assertIn("invalidated", msg)

    def test_otp_expiry(self):
        """Expired OTP (> 10 minutes) must be rejected."""
        plain_otp = SignupOTP.create_for_user(self.user)
        otp_record = SignupOTP.objects.filter(user=self.user).first()
        otp_record.expires_at = timezone.now() - timedelta(minutes=1)
        otp_record.save()

        success, msg = SignupOTP.verify(self.user, plain_otp)
        self.assertFalse(success)
        self.assertIn("expired", msg.lower())

    def test_otp_resend_cooldown(self):
        """Resend must enforce 60s cooldown."""
        SignupOTP.create_for_user(self.user)
        can_resend, reason = SignupOTP.can_resend(self.user)
        self.assertFalse(can_resend)
        self.assertIn("seconds before requesting", reason)

    def test_login_without_otp(self):
        """Active users log in with email and password only (no OTP)."""
        self.user.status = 'active'
        self.user.save()

        response = self.client.post('/accounts/login/', {
            'email': 'citizen@example.com',
            'password': 'SafePassword123!'
        })
        self.assertEqual(response.status_code, 302)
        # Check user is logged in
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_unverified_user_cannot_login_and_redirects_to_otp(self):
        """Unverified users trying to log in are redirected to OTP verification."""
        response = self.client.post('/accounts/login/', {
            'email': 'citizen@example.com',
            'password': 'SafePassword123!'
        })
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/verify-otp/', response.url)
