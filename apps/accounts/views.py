import json
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
from .forms import SignUpForm, LoginForm, UserProfileForm
from .models import UserProfile

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='apps.accounts.backends.EmailOrUsernameModelBackend')
            messages.success(request, f"Welcome to Digital To-Do & Wellness, {user.username}! Let's get you set up.")
            return redirect('dashboard:index')
    else:
        form = SignUpForm()
    
    return render(request, 'accounts/signup.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                next_url = request.GET.get('next', 'dashboard:index')
                messages.success(request, f"Welcome back, {user.username}!")
                return redirect(next_url)
            else:
                messages.error(request, "Invalid email/username or password. Please check your credentials.")
    else:
        form = LoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out successfully. Take care!")
    return redirect('accounts:login')


@login_required
def profile_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Your preferences and working hours have been saved!")
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=profile)
    
    return render(request, 'accounts/profile.html', {'form': form, 'profile': profile})


@login_required
@require_POST
def complete_onboarding_view(request):
    """Marks user onboarding walkthrough as completed and applies WHO guidelines."""
    try:
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        try:
            data = json.loads(request.body.decode('utf-8')) if request.body else {}
        except Exception:
            data = {}

        if data.get('age'):
            profile.age = int(data['age'])
        if data.get('activity_level'):
            profile.activity_level = data['activity_level']
        if data.get('hours_start'):
            profile.active_hours_start = datetime.time.fromisoformat(data['hours_start'])
        if data.get('hours_end'):
            profile.active_hours_end = datetime.time.fromisoformat(data['hours_end'])

        profile.onboarding_completed = True
        profile.apply_who_guidelines()
        profile.save()
        return JsonResponse({'success': True, 'message': 'Onboarding completed with WHO health profile set.'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
@require_POST
def save_push_subscription_view(request):
    """Saves the browser's Web Push subscription JSON payload."""
    try:
        data = json.loads(request.body.decode('utf-8'))
        subscription = data.get('subscription')
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        profile.push_subscription = subscription
        profile.save(update_fields=['push_subscription'])
        return JsonResponse({'success': True, 'message': 'Push notification subscription registered.'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)
