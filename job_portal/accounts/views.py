from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm
from .models import UserProfile

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

@login_required
def dashboard(request):
    try:
        profile = UserProfile.objects.get(user=request.user)
        user_type = profile.user_type
    except UserProfile.DoesNotExist:
        # Create profile if doesn't exist (default to applicant)
        profile = UserProfile.objects.create(user=request.user, user_type='applicant')
        user_type = 'applicant'
    
    if user_type == 'employer':
        return render(request, 'accounts/employer_dashboard.html', {'user_type': user_type})
    else:
        return render(request, 'accounts/applicant_dashboard.html', {'user_type': user_type})

# Add this new custom logout view
def custom_logout(request):
    """Custom logout view that accepts GET requests"""
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('login')