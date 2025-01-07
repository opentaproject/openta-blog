from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from blog.models import Post
import logging
logger = logging.getLogger(__name__)



def home(request):
    print(f"GET HOME.HTML")
    return render(request, 'home.html') 

@csrf_exempt
def lti_landing(request) :
    logger.error(f"LANDING {request.POST}")
    username = request.POST.get('custom_canvas_login_id',request.user.username)
    subdomain = request.POST.get('subdomain',None)
    request.session['username'] = username
    request.session['subdomain'] = subdomain
    request.session['roles'] = request.POST.get('roles',['Anonymous'])
    roles  =  request.POST.get('lti_roles','Anonymous')
    t = Post.AuthorType.ANONYMOUS
    td = 'Anonymous'
    if 'Student' in roles  or 'Learner' in roles :
        t = Post.AuthorType.STUDENT
        td = 'Student'
    if 'Teacher' in roles or 'Examiner' in roles or 'ContentDeveloper' in roles or 'TeachingAssistant' in roles  or 'Instructor' in roles:
        t = Post.AuthorType.TEACHER
        td = 'Teacher'
    if request.user.is_staff :
        t = Post.AuthorType.STAFF
        td = 'Admin'
    request.session['author_type'] = t
    request.session['author_type_display'] = td
    return redirect(f"/")

def config_lti(request):
    with open("backend/config.xml", "rb") as f:
        data = f.read()
    response = HttpResponse(data, content_type="text/xml")
    response["Content-Disposition"] = 'attachment; filename="config.xml"'
    return response
