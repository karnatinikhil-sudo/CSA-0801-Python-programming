from django import forms
from django.contrib.auth.models import User
from .models import UserProfile

class SignUpForm(forms.ModelForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'name@example.com', 'autofocus': 'autofocus'})
    )
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username or Nickname'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Create a password (at least 6 characters)'})
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm your password'})
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

    def clean_email(self):
        email = self.cleaned_data.get('email').strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email address already exists. Please log in instead.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username').strip()
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("This username is already taken. Please choose a different one.")
        return username

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match. Please re-enter them carefully.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    username = forms.CharField(
        label="Email or Username",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'name@example.com or username', 'autofocus': 'autofocus'})
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter your password'})
    )


class UserProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=150, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))

    class Meta:
        model = UserProfile
        fields = (
            'age', 'gender', 'weight_kg', 'activity_level',
            'active_hours_start', 'active_hours_end', 
            'hydration_interval_minutes', 'water_daily_target',
            'reminder_window_minutes', 'sound_alerts_enabled'
        )
        widgets = {
            'age': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '120', 'id': 'profile-age'}),
            'gender': forms.Select(attrs={'class': 'form-select', 'id': 'profile-gender'}),
            'weight_kg': forms.NumberInput(attrs={'class': 'form-control', 'min': '20', 'max': '250', 'step': '0.5', 'id': 'profile-weight'}),
            'activity_level': forms.Select(attrs={'class': 'form-select', 'id': 'profile-activity'}),
            'active_hours_start': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'active_hours_end': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'hydration_interval_minutes': forms.NumberInput(attrs={'class': 'form-control', 'min': '15', 'step': '15'}),
            'water_daily_target': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '30'}),
            'reminder_window_minutes': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'step': '1'}),
            'sound_alerts_enabled': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email

    def save(self, commit=True):
        profile = super().save(commit=commit)
        user = profile.user
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name = self.cleaned_data.get('last_name', '')
        user.email = self.cleaned_data.get('email', '')
        user.save()
        return profile
