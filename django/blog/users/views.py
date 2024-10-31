# Create your views here.
from django.shortcuts import render
from .models import Profile

def profile_view(request, username):
    profile = Profile.objects.get(user__username=username)
    return render(request, 'profile.html', {'profile': profile})
