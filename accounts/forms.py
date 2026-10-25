from django import forms
from django.contrib.auth import authenticate
from django.utils import timezone
from .models import User

INDIAN_STATES = [
    ('', 'Select State / Union Territory'),
    ('Central / All India', 'Central / All India'),
    ('Andhra Pradesh', 'Andhra Pradesh'),
    ('Arunachal Pradesh', 'Arunachal Pradesh'),
    ('Assam', 'Assam'),
    ('Bihar', 'Bihar'),
    ('Chhattisgarh', 'Chhattisgarh'),
    ('Delhi', 'Delhi (NCT)'),
    ('Goa', 'Goa'),
    ('Gujarat', 'Gujarat'),
    ('Haryana', 'Haryana'),
    ('Himachal Pradesh', 'Himachal Pradesh'),
    ('Jharkhand', 'Jharkhand'),
    ('Karnataka', 'Karnataka'),
    ('Kerala', 'Kerala'),
    ('Madhya Pradesh', 'Madhya Pradesh'),
    ('Maharashtra', 'Maharashtra'),
    ('Manipur', 'Manipur'),
    ('Meghalaya', 'Meghalaya'),
    ('Mizoram', 'Mizoram'),
    ('Nagaland', 'Nagaland'),
    ('Odisha', 'Odisha'),
    ('Punjab', 'Punjab'),
    ('Rajasthan', 'Rajasthan'),
    ('Sikkim', 'Sikkim'),
    ('Tamil Nadu', 'Tamil Nadu'),
    ('Telangana', 'Telangana'),
    ('Tripura', 'Tripura'),
    ('Uttar Pradesh', 'Uttar Pradesh'),
    ('Uttarakhand', 'Uttarakhand'),
    ('West Bengal', 'West Bengal'),
]

class SignupForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Choose a strong password (min 8 chars)'}),
        min_length=8,
        label='Password'
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Re-enter your password'}),
        min_length=8,
        label='Confirm Password'
    )
    consent = forms.BooleanField(
        required=True,
        label='I understand that Sarkari Saathi is an independent informational platform and does not submit forms or collect government credentials on my behalf.'
    )

    class Meta:
        model = User
        fields = ['name', 'email', 'language', 'state']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Your Full Name'}),
            'email': forms.EmailInput(attrs={'placeholder': 'name@example.com'}),
            'state': forms.Select(choices=INDIAN_STATES),
            'language': forms.Select(choices=[
                ('en', 'English'),
                ('hi', 'हिन्दी (Hindi)'),
                ('mwr', 'मारवाड़ी (Marwadi)'),
            ]),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email', '').lower().strip()
        if User.objects.filter(email=email, status='active').exists():
            raise forms.ValidationError("An active account with this email already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password')
        p2 = cleaned_data.get('confirm_password')
        if p1 and p2 and p1 != p2:
            self.add_error('confirm_password', "Passwords do not match.")
        return cleaned_data


class LoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'name@example.com'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Your password'}))

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email', '').lower().strip()
        password = cleaned_data.get('password')
        if email and password:
            user = authenticate(username=email, password=password)
            if not user:
                raise forms.ValidationError("Invalid email or password.")
            cleaned_data['user'] = user
        return cleaned_data
