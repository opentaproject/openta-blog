from django.shortcuts import render

def home(request):
    print(f"GET HOME.HTML")
    return render(request, 'home.html') 
