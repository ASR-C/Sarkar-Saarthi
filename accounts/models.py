import hmac
import hashlib
import secrets
from datetime import timedelta
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email address is required')
        email = self.normalize_email(email)
        extra_fields.setdefault('status', 'unverified')
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('status', 'active')
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    STATUS_CHOICES = (
        ('unverified', 'Unverified'),
        ('active', 'Active'),
    )

    email = models.EmailField('Email Address', unique=True, max_length=255)
    name = models.CharField('Full Name', max_length=150)
    language = models.CharField('Preferred Language', max_length=10, default='en')
    state = models.CharField('State / UT', max_length=100, blank=True)
    status = models.CharField('Account Status', max_length=20, choices=STATUS_CHOICES, default='unverified')
    consent_at = models.DateTimeField('Consent Given At', null=True, blank=True)
    created_at = models.DateTimeField('Created At', auto_now_add=True)
    
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f"{self.name} <{self.email}>"


class SignupOTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='signup_otps')
    otp_hash = models.CharField(max_length=128)
    expires_at = models.DateTimeField()
    attempts = models.PositiveIntegerField(default=0)
    used_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'signup_otps'
        ordering = ['-created_at']
        verbose_name = 'Signup OTP'
        verbose_name_plural = 'Signup OTPs'

    @classmethod
    def hash_otp(cls, plain_otp: str) -> str:
        """Hashed with HMAC using the server SECRET_KEY so OTP is never in plain text."""
        return hmac.new(
            settings.SECRET_KEY.encode('utf-8'),
            plain_otp.strip().encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

    @classmethod
    def create_for_user(cls, user: User) -> str:
        """Generates a secure 6-digit OTP using secrets module, stores HMAC hash, and returns plain OTP."""
        # 6 digits: 100000 to 999999
        plain_otp = f"{secrets.randbelow(900000) + 100000}"
        otp_hash = cls.hash_otp(plain_otp)
        expires_at = timezone.now() + timedelta(minutes=10)
        cls.objects.create(
            user=user,
            otp_hash=otp_hash,
            expires_at=expires_at,
            attempts=0
        )
        return plain_otp

    @classmethod
    def can_resend(cls, user: User) -> tuple[bool, str]:
        """Rules: 60 seconds cooldown between resends, maximum 5 sends per email per hour."""
        now = timezone.now()
        one_hour_ago = now - timedelta(hours=1)
        recent_in_hour = cls.objects.filter(user=user, created_at__gte=one_hour_ago).count()
        if recent_in_hour >= 5:
            return False, "Maximum 5 OTP requests per hour reached. Please try again later."
        
        last_otp = cls.objects.filter(user=user).order_by('-created_at').first()
        if last_otp and (now - last_otp.created_at).total_seconds() < 60:
            remaining = int(60 - (now - last_otp.created_at).total_seconds())
            return False, f"Please wait {remaining} seconds before requesting a new OTP."
        
        return True, ""

    @classmethod
    def verify(cls, user: User, entered_otp: str) -> tuple[bool, str]:
        """
        Verifies entered OTP against the latest active record.
        Enforces:
        - 10 minutes expiry
        - Max 5 wrong attempts then invalidated
        - Cannot be reused
        """
        now = timezone.now()
        latest = cls.objects.filter(user=user, used_at__isnull=True).order_by('-created_at').first()
        if not latest:
            return False, "No active OTP found. Please request a new code."

        if latest.attempts >= 5:
            return False, "Too many wrong attempts. This OTP has been invalidated. Please request a new code."

        if now > latest.expires_at:
            return False, "This OTP has expired. Please request a new code."

        expected_hash = cls.hash_otp(entered_otp)
        if hmac.compare_digest(latest.otp_hash, expected_hash):
            latest.used_at = now
            latest.save(update_fields=['used_at'])
            user.status = 'active'
            user.save(update_fields=['status'])
            return True, "Verification successful."
        else:
            latest.attempts += 1
            latest.save(update_fields=['attempts'])
            remaining = 5 - latest.attempts
            if remaining <= 0:
                return False, "Incorrect OTP. Maximum attempts reached. OTP is now invalidated."
            return False, f"Incorrect OTP. {remaining} attempt(s) remaining."
