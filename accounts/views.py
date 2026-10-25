from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from django.utils import timezone
from .models import User, SignupOTP
from .forms import SignupForm, LoginForm
from .services import send_signup_otp_email

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('core:home')

    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            # Reuse unverified user if exists, or create new
            user = User.objects.filter(email=email, status='unverified').first()
            if not user:
                user = form.save(commit=False)
                user.status = 'unverified'
            else:
                user.name = form.cleaned_data['name']
                user.language = form.cleaned_data['language']
                user.state = form.cleaned_data['state']
            
            user.set_password(form.cleaned_data['password'])
            user.consent_at = timezone.now()
            user.save()

            # Generate OTP & Send Email
            plain_otp = SignupOTP.create_for_user(user)
            send_signup_otp_email(user, plain_otp)

            request.session['pending_user_id'] = user.id
            messages.success(request, f"A 6-digit verification code has been sent to {user.email}.")
            return redirect('accounts:verify_otp')
    else:
        form = SignupForm(initial={'language': request.session.get('lang', 'en')})

    return render(request, 'accounts/signup.html', {'form': form})


def verify_otp_view(request):
    user_id = request.session.get('pending_user_id')
    if not user_id:
        messages.warning(request, "No pending registration found. Please sign up or log in.")
        return redirect('accounts:signup')

    user = User.objects.filter(id=user_id).first()
    if not user:
        request.session.pop('pending_user_id', None)
        return redirect('accounts:signup')

    if user.status == 'active':
        login(request, user)
        request.session.pop('pending_user_id', None)
        return redirect('core:home')

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'resend':
            can_send, reason = SignupOTP.can_resend(user)
            if can_send:
                plain_otp = SignupOTP.create_for_user(user)
                send_signup_otp_email(user, plain_otp)
                messages.success(request, "A fresh 6-digit OTP has been sent.")
            else:
                messages.error(request, reason)
            return redirect('accounts:verify_otp')

        entered_otp = request.POST.get('otp', '').strip()
        success, message = SignupOTP.verify(user, entered_otp)
        if success:
            login(request, user)
            request.session['lang'] = user.language
            request.session.pop('pending_user_id', None)
            messages.success(request, "Email verified successfully! Welcome to Sarkari Saathi.")
            return redirect('core:home')
        else:
            messages.error(request, message)

    return render(request, 'accounts/verify_otp.html', {'user': user})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('core:home')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            if user.status == 'unverified':
                request.session['pending_user_id'] = user.id
                can_send, _ = SignupOTP.can_resend(user)
                if can_send:
                    plain_otp = SignupOTP.create_for_user(user)
                    send_signup_otp_email(user, plain_otp)
                messages.info(request, "Please verify your email address to activate your account.")
                return redirect('accounts:verify_otp')

            login(request, user)
            request.session['lang'] = user.language
            messages.success(request, f"Welcome back, {user.name}!")
            next_url = request.GET.get('next')
            return redirect(next_url if next_url else 'core:home')
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out safely.")
    return redirect('core:home')
