from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UserChangeForm
from django.contrib import messages
from django.urls import reverse
from django.views.decorators.http import require_POST

User = get_user_model()

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful.")
            return redirect('profile')
        else:
            messages.error(request, "Registration failed. Please correct the errors below.")
    else:
        form = UserCreationForm()
    return render(request, 'users/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "Logged in successfully.")
            return redirect('profile')
        else:
            messages.error(request, "Login failed. Please check your username and password.")
    else:
        form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, "Logged out successfully.")
    return redirect('login')

@login_required
def profile_view(request):
    return render(request, 'users/profile.html', {'user': request.user})

@login_required
def user_list_view(request):
    users = User.objects.all()
    return render(request, 'users/user_list.html', {'users': users})

@login_required
def user_detail_view(request, user_id):
    user_obj = get_object_or_404(User, id=user_id)
    return render(request, 'users/user_detail.html', {'user_obj': user_obj})

@login_required
def user_update_view(request):
    if request.method == 'POST':
        form = UserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('profile')
        else:
            messages.error(request, "Update failed. Please correct the errors below.")
    else:
        form = UserChangeForm(instance=request.user)
    return render(request, 'users/user_update.html', {'form': form})

@login_required
@require_POST
def user_delete_view(request):
    user = request.user
    logout(request)
    user.delete()
    messages.info(request, "Your account has been deleted.")
    return redirect('register')
