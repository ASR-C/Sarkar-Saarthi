from django.contrib import admin
from .models import User, SignupOTP

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'name', 'language', 'state', 'status', 'is_staff', 'created_at')
    list_filter = ('status', 'language', 'is_staff')
    search_fields = ('email', 'name', 'state')
    readonly_fields = ('consent_at', 'created_at')

@admin.register(SignupOTP)
class SignupOTPAdmin(admin.ModelAdmin):
    list_display = ('user', 'attempts', 'expires_at', 'used_at', 'created_at')
    list_filter = ('used_at',)
    search_fields = ('user__email',)
    readonly_fields = ('otp_hash', 'created_at', 'expires_at')
