#igallery/gallery/views.py
import os
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login as auth_login, logout as auth_logout, load_backend
from django.contrib.auth.forms import AuthenticationForm
from django.conf import settings
from django.contrib import messages

from .models import UserProfile

import requests
from django.contrib.auth.models import User  # Import the User model

# Replace these with your actual Instagram app credentials
INSTAGRAM_AUTH_SETTINGS = {
    # 'CLIENT_ID': '738187601725581',
    # 'CLIENT_SECRET': '39c13bd04628d971b06c33b4da24a903',
    'REDIRECT_URI': 'https://localhost:8000/instagram/callback/',  # Adjust if needed
    'SCOPE': ['user_profile', 'user_media'],
}

def instagram_login(request):
    """Redirects the user to Instagram for authentication."""
    client_id = os.getenv('INSTAGRAM_CLIENT_ID')
    redirect_uri = INSTAGRAM_AUTH_SETTINGS['REDIRECT_URI']
    scope = ','.join(INSTAGRAM_AUTH_SETTINGS['SCOPE']) 

    auth_url = (
        f'https://api.instagram.com/oauth/authorize'
        f'?client_id={client_id}'
        f'&redirect_uri={redirect_uri}'
        f'&scope={scope}'  # Make sure scope is a comma-separated string
        f'&response_type=code'
    )
    return redirect(auth_url)

def instagram_callback(request):
    """Handles the Instagram callback and user creation/login."""
    
    code = request.GET.get('code')

    if not code:
        error_message = request.GET.get('error_description', 'Unknown error during Instagram authentication.')
        return render(request, 'gallery/login.html', {'error': error_message})

    client_id = os.getenv('INSTAGRAM_CLIENT_ID')
    client_secret = os.getenv('INSTAGRAM_CLIENT_SECRET')
    redirect_uri = INSTAGRAM_AUTH_SETTINGS['REDIRECT_URI']

    # Exchange the code for an access token
    access_token_url = f'https://api.instagram.com/oauth/access_token'
    data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'authorization_code',
        'redirect_uri': redirect_uri,
        'code': code
    }
    try:
        response = requests.post(access_token_url, data=data)  # Use POST request
        response.raise_for_status()

        response_data = response.json()
        access_token = response_data.get('access_token')
        user_id = response_data.get('user_id')

        if not access_token or not user_id:
            return render(request, 'gallery/login.html', {'error': 'Failed to retrieve access token from Instagram.'})

        # Fetch user profile data
        user_profile_url = f'https://graph.instagram.com/{user_id}?fields=id,username&access_token={access_token}'
        profile_response = requests.get(user_profile_url)
        profile_response.raise_for_status() 

        profile_data = profile_response.json()
        instagram_username = profile_data.get('username')

        if not instagram_username:
            return render(request, 'gallery/login.html', {'error': 'Failed to retrieve user profile from Instagram.'})

        # Get or create the user in your Django database
        user, created = User.objects.get_or_create(username=instagram_username)
        if created:
            # Set a default password or generate a random one for the new user
            user.set_password('default_password') 
            user.save()
            
        # Save (or update) the access token in the UserProfile
        user_profile, created = UserProfile.objects.get_or_create(user=user)
        user_profile.instagram_access_token = access_token 
        user_profile.save()

        # Log the user in
        auth_login(request, user)
        messages.success(request, f"Welcome, {instagram_username}!")
        return redirect('index') # Redirect to your index view

    except requests.exceptions.RequestException as e:
        error_message = f'Error communicating with Instagram: {e}'
        return render(request, 'gallery/login.html', {'error': error_message})
    
def login(request):
    """Handles both standard and Instagram logins."""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return redirect('/')
    else:
        form = AuthenticationForm(request)
    context = {'form': form}  # No need for Instagram keys here
    return render(request, 'gallery/login.html', context)

@login_required
def index(request):
    return render(request, 'gallery/index.html')

def logout(request):
    auth_logout(request)
    return redirect('login')

def get_user_access_token(user):
    """Retrieves the Instagram access token for the given user."""
    try:
        user_profile = user.userprofile  
        return user_profile.instagram_access_token
    except UserProfile.DoesNotExist:
        return None

@login_required
def gallery(request):
    user_posts = []
    access_token = None  

    if request.user.is_authenticated:
        access_token = get_user_access_token(request.user)

    if access_token:
        next_max_id = None
        while True:
            url = f"https://graph.instagram.com/me/media?fields=id,caption,media_url&access_token={access_token}"
            if next_max_id:
                url += f"&after={next_max_id}"
            
            try:
                response = requests.get(url)
                response.raise_for_status()

                data = response.json()
                user_posts.extend(data.get('data', []))

                # Check for pagination
                paging = data.get('paging', {})
                next_max_id = paging.get('cursors', {}).get('after') 

                if not next_max_id:  # No more pages
                    break
            except requests.exceptions.RequestException as e:
                messages.error(request, f'Error fetching Instagram posts: {e}')
                break  # Stop if there is an error

    context = {'user_posts': user_posts}
    return render(request, 'gallery/gallery.html', context)

@login_required
def saved_pictures(request):
    saved_pictures = []
    access_token = None

    if request.user.is_authenticated:
        access_token = get_user_access_token(request.user)

    if access_token:
        try:
            url = f"https://graph.instagram.com/me/saved?fields=id,caption,media_url&access_token={access_token}"
            response = requests.get(url)
            response.raise_for_status()

            data = response.json()
            saved_pictures = data.get('data', [])

        except requests.exceptions.RequestException as e:
            messages.error(request, f'Error fetching saved pictures: {e}')

    context = {'saved_pictures': saved_pictures}
    return render(request, 'gallery/saved_pictures.html', context)