from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

def home(request):
    print(f"GET HOME.HTML")
    return render(request, 'home.html') 

@csrf_exempt
def lti_landing(request) :
    print(f"LANDING {request.POST}")
    username = request.POST.get('custom_canvas_login_id',request.user.username)
    subdomain = request.POST.get('subdomain',None)
    request.session['username'] = username
    request.session['subdomain'] = subdomain
    return redirect(f"/")

def config_lti(request):
    with open("backend/config.xml", "rb") as f:
        data = f.read()
    response = HttpResponse(data, content_type="text/xml")
    response["Content-Disposition"] = 'attachment; filename="config.xml"'
    return response
