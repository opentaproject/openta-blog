from django.shortcuts import render
from django.http import HttpResponse

def home(request):
    print(f"GET HOME.HTML")
    return render(request, 'home.html') 

def config_lti(request):
    with open("backend/config.xml", "rb") as f:
        data = f.read()
    response = HttpResponse(data, content_type="text/xml")
    response["Content-Disposition"] = 'attachment; filename="config.xml"'
    return response
