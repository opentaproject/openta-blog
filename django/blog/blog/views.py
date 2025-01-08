# blogs/views.py
from django.db.models import Count, Subquery, Sum, OuterRef, F
import hmac
import hashlib
import urllib.parse
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from blog.models import Post, Comment, Category,Visit
from django.db import ProgrammingError
from blog.forms import CommentForm, PostForm
from rest_framework.decorators import api_view
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseForbidden
from django.views.decorators.clickjacking import xframe_options_exempt
import time, base64
import logging
import json
from django.http import JsonResponse
from oauthlib.oauth1 import RequestValidator
logger = logging.getLogger(__name__)
from oauthlib.oauth1 import RequestValidator


#def create_signature_base_string(http_method, base_url, params):
#    encoded_base_url = base_url ; # percent_encode(base_url)
#    sorted_params = sorted((k), percent_encode(v)) for k, v in params.items())
#    normalized_params = '&'.join(f'{k}={v}' for k, v in sorted_params)
#    encoded_params = percent_encode(normalized_params)
#    return f'{http_method.upper()}&{encoded_base_url}&{encoded_params}'
#
#def create_signing_key(consumer_secret, token_secret=''):
#    return f'{percent_encode(consumer_secret)}&{percent_encode(token_secret)}'

def generate_base_string(method, base_url, params):
    # Ensure parameters are percent-encoded and sorted
    encoded_params = urllib.parse.urlencode(sorted(params.items()), quote_via=urllib.parse.quote)
    # Construct the base string
    base_string = '&'.join([
        method.upper(),
        urllib.parse.quote(base_url, safe=''),
        urllib.parse.quote(encoded_params, safe='')
    ])
    return base_string

def validate_oauth_signature(method, base_url, params, consumer_secret, token_secret=None, received_signature=None):

    def generate_base_string(method, base_url, params):
        encoded_params = urllib.parse.urlencode(sorted(params.items()), quote_via=urllib.parse.quote)
        base_string = '&'.join([
            method.upper(),
            urllib.parse.quote(base_url, safe=''),
            urllib.parse.quote(encoded_params, safe='')
        ])
        return base_string

    print(f"PARAMS = {params}")
    base_string = generate_base_string(method, base_url, params)
    signing_key = f"{urllib.parse.quote(consumer_secret, safe='')}&{urllib.parse.quote(token_secret, safe='') if token_secret else ''}"
    hashed = hmac.new(signing_key.encode('utf-8'), base_string.encode('utf-8'), hashlib.sha1)
    print(f"HASHED = {hashed}")
    generated_signature = base64.b64encode( hashed.digest() )
    print(f"GENERATED_SIGNATUE = {generated_signature}")
    return True
    #return hmac.compare_digest(generated_signature, received_signature)
    #request_method = 'POST'
    #base_url = 'https://your.tool.url/launch'
    #params = {
    #    'oauth_consumer_key': 'your_consumer_key',
    #    'oauth_token': 'your_token',
    #    'oauth_signature_method': 'HMAC-SHA1',
    #    'oauth_timestamp': 'timestamp',
    #    'oauth_nonce': 'nonce',
    #    # Include all other LTI parameters here
    #}
    #consumer_secret = settings.LTI_SECRET
    #received_signature = 'signature_from_request'
    #is_valid = validate_oauth_signature(request_method, base_url, params, consumer_secret, token_secret, received_signature)



def create_oauth_signature(http_method, base_url, params, consumer_secret, token_secret=''):
    def percent_encode(s):
        return urllib.parse.quote(s, safe='')
    def create_signature_base_string(http_method, base_url, params):
        encoded_base_url = percent_encode(base_url)
        sorted_params = ((percent_encode(k), percent_encode(v)) for k, v in params.items() if not k == 'oauth_signature')
        normalized_params = '&'.join(f'{k}={v}' for k, v in sorted_params)
        encoded_params = percent_encode(normalized_params)
        return f'{http_method.upper()}&{encoded_base_url}&{encoded_params}'

    def create_signing_key(consumer_secret, token_secret=''):
        return f'{percent_encode(consumer_secret)}&{percent_encode(token_secret)}'

    signature_base_string = create_signature_base_string(http_method, base_url, params)
    print(f"SIGNATURE_BASE_STRING {signature_base_string}")
    signing_key = create_signing_key(consumer_secret, token_secret)
    hashed = hmac.new(signing_key.encode(), signature_base_string.encode(), hashlib.sha1)
    signature = base64.b64encode(hashed.digest()).decode()
    return signature



def get_username( request ):
    return request.session.get('username',request.user.username)

def get_author_type( request ):
    roles  =  request.POST.get('lti_roles',request.POST.get('roles',['Anonymous']) )
    print(f"ROLES = {roles}")
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
    request.session['author_type'] = td;
    request.session['author_type_display'] = td
    return td

def load_session_variables( request , *args, **kwargs ):
    logger.error(f"LOAD SESSION_VARIABLES {args} {kwargs} ")
    if request.data :
        params = {};
        for key in ['oauth_consumer_key','oauth_nonce','oauth_timestamp','oauth_signature_method','oauth_version','lti_message_type','lti_version','resource_link_id' ]:
            params[key] = request.data.get(key,None)
        validate_oauth_signature('POST', "https://www.openta.se", params ,settings.LTI_SECRET )
        t = str( int(  time.time() )).encode() ;
        bt = base64.b64encode(t)
        logger.error(f"T = {t}")
        logger.error(f"BT = {bt}")
        data = request.data
        data_ = {
            'lti_message_type': 'basic-lti-launch-request',
            'lti_version': 'LTI-1p0',
	        'subdomain': 'ffm516-2024',
            'resource_link_id': 'resourceLinkId',
	        'custom_canvas_login_id': 'ulf',
	        'lis_person_name_contact_email_primary': 'ulf@chalmers.se',
	        'roles': 'Instructor,ContentDeveloper,TeachingAssistant',
	        'resource_link_title': 'ffm516-2024',
            'oauth_consumer_key': '889d570f472',
            'oauth_nonce': bt.strip() ,
            'oauth_signature_method': 'HMAC-SHA1',
            'oauth_timestamp': t,
            'oauth_version': '1.0'
        };



        odata = {
            'lti_message_type': 'basic-lti-launch-request',
            'lti_version': 'LTI-1p0',
            'subdomain': 'ffm516-2024',
            'resource_link_id': 'resourceLinkId',
	        'custom_canvas_login_id': 'ulf',
	        'lis_person_name_contact_email_primary': 'ulf@chalmers.se',
            'roles': 'Instructor,ContentDeveloper,TeachingAssistant',
	        'resource_link_title': 'ffm516-2024',
            'oauth_consumer_key': '889d570f472',
            'oauth_nonce': bt.strip() ,
            'oauth_signature_method': 'HMAC-SHA1',
            'oauth_timestamp': t,
            'oauth_version': '1.0'
        };
        logger.error(f"DATA EXISTS {request.data}")
        logger.error(f"DATA_ = {data_}")
        timestamp = data_['oauth_timestamp']
        client_key = request.data.get('oauth_consumer_key',None)
        client_signature = request.data.get('oauth_signature',None)
        client_timestamp = request.data.get('oauth_timestamp',None)
        client_key_ok =  client_key  == settings.LTI_KEY 
        logger.error(f"OK CLIENT KEY?  { client_key_ok }")
        logger.error(f"OK TIMESTAMP ? {timestamp}=={ client_timestamp} ")
        method = 'POST'
        url = "http://localhost:8000"
        consumer_key = settings.LTI_KEY
        consumer_secret = settings.LTI_SECRET
        signature = create_oauth_signature(method, url, params , consumer_secret ) # , consumer_secret)
        signature_ = create_oauth_signature(method, url, data_, consumer_secret) # , consumer_secret)
        osignature = create_oauth_signature(method, url, odata, consumer_secret) # , consumer_secret)
        logger.error(f"SIGNATURES = {client_signature }  {signature} {signature_} {osignature} ")
        
    pk = kwargs.get('pk',None)
    request.session['is_staff'] = False
    category_selected = args[1].get('category_selected',request.session.get('category_selected',None ) )
    if request.user and request.user.username  :
        username = request.user.username
        request.session['username'] = username
        request.session['is_staff'] = request.user.is_staff
        request.session['is_authenticated'] = True
    if category_selected == None :
        category_selected = Category.objects.all()[0].pk
    if not pk == None :
        category_selected = Post.objects.get(pk=pk).category.pk;
    #for key in request.session.keys() :
    #    logger.error(f" {key} {request.session[key]}")
    if request.method == 'POST' :
        author_type = get_author_type( request )
        data = dict( request.POST )
        print(f"DATA = {data}")
        username = data.get('custom_canvas_login_id', [''])[0]
        subdomain = data.get('resource_link_title', [''])[0]
        request.session['username'] = username
        request.session['is_authenticated'] = not username ==  ''
        request.session['subdomain'] = subdomain
        request.session['category_selected'] =  category_selected
    else :
        if 'username' in request.session :
            username = request.session['username']
        else :
            username = request.GET.get('user',request.user.username)
        request.session['username'] = username
        request.session['is_authenticated'] = not username == ''
        request.session['category_selected'] =  category_selected
    for v in request.session.keys():
        logger.error(f"{v} = {request.session[v]}")
    category_selected = request.session['category_selected']
    author_type = request.session['author_type']
    logger.error(f"ARGS = {args}")
    logger.error(f"KWARGS = {kwargs}")
    logger.error(f"DATA = {request.data}")
    logger.error(f"CATEGORY_SELECTED = {category_selected}")
    logger.error(f"AUTHORTYPE = {author_type}")
    return True





@api_view(["GET", "POST"])
@xframe_options_exempt  # N
def blog_index(request, *args, **kwargs ) :
    logger.error(f"BLOG_INDEX METHOD = {request.method}")
    pk = kwargs.get('pk',None)
    #category_selected = kwargs.get('category_selected',request.session.get('category_selected',None ) )
    logger.error(f"PK = {pk}")
    if not load_session_variables( request, args, kwargs ) :
        return HttpResponseForbidden("AJABAJA")
        
    category_selected = request.session['category_selected']
    username = request.session['username']
    #category_selected = request.session['category_selected']
    logger.error(f"CATEGORY_SELECTED = {category_selected}")
    subdomain = request.session['subdomain']
    #request.session['is_staff'] = False
    #if request.user and request.user.username  :
    #    username = request.user.username
    #    request.session['username'] = username
    #    request.session['is_staff'] = request.user.is_staff
    #    request.session['is_authenticated'] = True
    #if category_selected == None :
    #    category_selected = Category.objects.all()[0].pk
    #if not pk == None :
    #    category_selected = Post.objects.get(pk=pk).category.pk;
    ##for key in request.session.keys() :
    ##    logger.error(f" {key} {request.session[key]}")
    #if request.method == 'POST' :
    #    author_type = get_author_type( request )
    #    data = dict( request.POST )
    #    username = data.get('custom_canvas_login_id', [''])[0]
    #    subdomain = data.get('resource_link_title', [''])[0]
    #    request.session['username'] = username
    #    request.session['is_authenticated'] = not username ==  ''
    #    request.session['subdomain'] = subdomain
    #    request.session['category_selected'] =  category_selected
    #else :
    #    if 'username' in request.session :
    #        username = request.session['username']
    #    else :
    #        username = request.GET.get('user',request.user.username)
    #    request.session['username'] = username
    #    request.session['is_authenticated'] = not username == ''
    #    request.session['category_selected'] =  category_selected
    subdomain = request.session.get('subdomain',None )
    if subdomain and not Category.objects.filter(name=subdomain) :
        new_category = Category.objects.create(name=subdomain,restricted=True)
        new_category.save() 

    try :
        comments  = []
        posts = Post.objects.all().order_by("-created_on").filter(category__pk=category_selected).annotate(viewed=Count('comment') )
        for post in posts :
            if post.body == '' : ## THERE SHOULD BE BETTER WAY TO ENFORCE NONEMPTY BODY
                post.delete()
        post_subquery = Post.objects.filter(id=OuterRef('id'),author=username).annotate(viewed=Count('author')).values('viewed')
        visit_subquery = Visit.objects.filter(post=OuterRef('id'),visitor=username).annotate(viewed=Count('visitor')).values('viewed')
        visit_subquery = Visit.objects.filter(post=OuterRef('id'),visitor=username,  post__last_modified__lt=F('date') ).annotate(viewed=Count('visitor') ).values('viewed')
        posts = Post.objects.all().order_by("-created_on").filter(category__pk=category_selected).annotate(viewed=Subquery(visit_subquery)  )
        if request.session['is_staff'] :
            categories = Category.objects.all()
        else :
            copen = Category.objects.all().filter(restricted=False)
            closed = Category.objects.all().filter(restricted=True,name=subdomain)
            categories = ( closed | copen )
        categories = categories.order_by ('restricted')
        cat = int( category_selected )



        is_authenticated = request.session.get('is_authenticated',False)
        is_staff = request.session.get('is_staff',False)
        #if pk == None :
        #    pk = request.session.get('last_post_pk', None )
        if posts :
            if pk == None :
                selected_posts = []
            else :
                selected_posts = posts.filter(pk=pk)
        else :
            pk = None;
            selected_posts = []

        for post in selected_posts :
            visit = Visit.objects.update_or_create(visitor=username,post=post)
            comments = Comment.objects.filter(post=post ).order_by('-created_on')
        author_type = request.session.get('author_type', Post.AuthorType.ANONYMOUS )
        author_type_display = request.session.get('author_type_display','Anonymous')
        if request.user.is_staff :
            author_type = Post.AuthorType.STAFF
            author_type_display = 'Admin'
        context = {
            "posts": posts,
            "categories":  categories,
            "subdomain" : subdomain, 
            "category_selected" : cat,
            "is_authenticated" : is_authenticated,
            "visibility" : Post.Visibility.PUBLIC , 
            "author_type" : author_type,
            "author_type_display" : author_type_display,
            "is_staff" : is_staff,
            "username" : username,
            "selected" : pk,
            "selected_posts" : selected_posts,
            "comments" : comments,
        }
    except ProgrammingError as e:
        context = {
            "posts" : [],
            "categoies" : [],
            "category_selected" : None
            }
        logger.error(f"ERROR = {type(e).__name__} {str(e)}")
    request.session['last_post_pk'] = pk

    return render(request, "blog/sidebyside.html", context)

def blog_category(request, category):
    posts = Post.objects.filter(
        category__name__contains=category
    ).order_by("-created_on")
    context = {
        "category": category,
        "posts": posts,
    }
    return render(request, "blog/category.html", context)


@api_view(["GET", "POST"])
@xframe_options_exempt  # N
def blog_add_post(request ):
    username = request.session.get('username',None)
    is_authenticated = request.session.get('is_authenticated',False)
    if not is_authenticated :
        raise PermissionDenied("You must be authenticated in to add a post")
        
    author = username
    try :
        category_ = request.POST.get('category')[0]
        category = Category.objects.get(pk=category_)
    except ObjectDoesNotExist as e :
        category = Category.objects.all()[0].pk
    post, _  = Post.objects.get_or_create(title='',body='',category=category)
    if request.method == "POST":
        is_staff = request.session.get('is_staff',False)
        form = PostForm( request.POST, is_staff=is_staff, instance=post)
        if form.is_valid() :
            form.save()  # S
            form.save()
            return HttpResponseRedirect(f'/edit_post/{post.pk}')
        else :
            pass
    else :
        form = PostForm( is_staff=is_staff, instance=post)
    return render(request, "blog/blog_edit_post.html", {'form' : form, 'is_staff' : is_staff  } )

@api_view(["GET", "POST"])
@xframe_options_exempt  # N
def blog_delete_post(request, pk ):
    if not request.session.get('is_authenticated',False ):
        raise PermissionDenied("You must be authenticated in to edit a post")
    post = get_object_or_404(Post, pk=pk)
    username = request.session.get('username',None)
    category_selected = post.category.pk
    post.delete();
    return HttpResponseRedirect(f'/blog/{category_selected}')




@api_view(["GET", "POST"])
@xframe_options_exempt  # N
def blog_edit_post(request, pk ):
    if not request.session.get('is_authenticated',False ):
        raise PermissionDenied("You must be authenticated in to edit a post")
    action = request.POST.get('action','edit');
    post = get_object_or_404(Post, pk=pk)
    username = request.session.get('username',None)
    is_staff = request.session.get('is_staff',False)

    if request.method == "POST":
        if action == 'delete' :
            post.delete();
            return HttpResponseRedirect(f'/')

        form = PostForm( request.POST, is_staff=is_staff,instance=post)
        if form.is_valid() and not post.body == '' :
            form.save()  # S
            form.save()
            return HttpResponseRedirect(f'/post/{post.pk}')
        else :
            pass
    else :
        form = PostForm( is_staff=is_staff, instance=post)
        return render(request, "blog/blog_edit_post.html", {'form' : form, 'is_staff' : is_staff   } )




@api_view(["GET", "POST"])
@xframe_options_exempt  # N
def blog_leave_comment (request, pk):

    post = Post.objects.get(pk=pk)
    post_pk = pk
    username = get_username(request) 
    author = username
    body = ''
    comment , _ = Comment.objects.get_or_create(author=author,post=post,body=body)
    if request.method == "POST":
        form = CommentForm( request.POST, instance=comment)
        if form.is_valid() and form.instance.body != '' and form.instance.author != '':
            form.save()  # S
            form.save()
            return HttpResponseRedirect(f'/post/{comment.post.pk}')
        else :
            pass
    else :
        form = CommentForm( instance=comment)
    return render(request, "blog/blog_edit_comment.html", {'form' : form, 'username' : username   } )




@api_view(["GET", "POST"])
@xframe_options_exempt  # N
def blog_edit_comment(request, pk ):
    comment = get_object_or_404(Comment, pk=pk)
    username = get_username(request)
    action = request.POST.get('action','edit');
    post = comment.post
    if comment.body in [ '<p>&nbsp;</p>' ,'']  :
        comment.delete();
        return HttpResponseRedirect(f'/post/{comment.post.pk}')

    if request.method == "POST":
        if  action == 'delete' :
            comment.delete();
            return HttpResponseRedirect(f'/post/{comment.post.pk}')

        form = CommentForm( request.POST, instance=comment)
        if form.is_valid():
            form.save()  # S
            form.save()
            return HttpResponseRedirect(f'/post/{comment.post.pk}')
        else :
            pass
    else :
        form = CommentForm( instance=comment)
    return render(request, "blog/blog_edit_comment.html", {'form' : form, 'username' : username   } )


@api_view(["GET", "POST"])
@xframe_options_exempt  # N
def blog_delete_comment(request, pk ):
    comment = get_object_or_404(Comment, pk=pk)
    username = request.user.username
    action = request.POST.get('action','edit');
    post = comment.post
    comment.delete();
    return HttpResponseRedirect(f'/post/{post.pk}')

