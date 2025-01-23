# blogs/views.py
from django.db.models import Count, Subquery, Sum, OuterRef, F
import hmac
import hashlib
import urllib.parse
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from blog.models import Post, Comment, Category,Visit,Visitor,Subdomain, FilterKey
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
from backend.oauth1 import load_session_variables, get_author_type, get_username
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt






@api_view(["GET", "POST"])
@csrf_exempt
#@xframe_options_exempt  
def blog_index(request, *args, **kwargs ) :
    pk = kwargs.get('pk',None)
    #category_selected = kwargs.get('category_selected',request.session.get('category_selected',None ) )
    if not load_session_variables( request, args, kwargs ) :
        return HttpResponseForbidden("AJABAJA")
    referer =  request.session.get('referer','')
    name = str( request.session.get('filter_key','')  )
    filter_title = request.session.get('filter_title','')
    filter_key , _  = FilterKey.objects.get_or_create(name=name)
    filter_key.title = filter_title
    filter_key.save()
    category_selected = request.session['category_selected']
    username = request.session['username']
    subdomain = request.session.get('subdomain','default')
    filter_title = request.session.get('filter_title','')
    subd, _ = Subdomain.objects.get_or_create(name=subdomain)
    if subdomain and not Category.objects.filter(name=subdomain) :
        new_category = Category.objects.create(name=subdomain,restricted=True)
        new_category.save() 
    if not filter_key.name   == '' :
        category_selected =  Category.objects.get(name=subdomain ).pk
    try :
        visitor, _ = Visitor.objects.update_or_create(name=username,subdomain=subd,visitor_type=1)
        comments  = []
        posts = Post.objects.all().order_by("-created_on").filter(category__pk=category_selected).annotate(viewed=Count('comment') )
        for post in posts :
            if post.body == '' : ## THERE SHOULD BE BETTER WAY TO ENFORCE NONEMPTY BODY
                post.delete()
        post_subquery = Post.objects.filter(id=OuterRef('id'),post_author=visitor).annotate(viewed=Count('post_author')).values('viewed')
        #visit_subquery = Visit.objects.filter(post=OuterRef('id'),visitor=visitor,  post__last_modified__lt=F('date') ).annotate(viewed=Count('visitor') ).values('viewed')
        visit_subquery = Visit.objects.filter(post=OuterRef('id'),visitor=visitor,  post__last_modified__lt=F('date') ).annotate(viewed=Count('visitor') ).values('viewed')
        posts = Post.objects.all().order_by("-created_on").filter(category__pk=category_selected).annotate(viewed=Subquery(visit_subquery)  )
        if request.session['is_staff'] :
            categories = Category.objects.all()
        else :
            copen = Category.objects.all().filter(restricted=False)
            closed = Category.objects.all().filter(restricted=True,name=subdomain)
            categories = ( closed | copen )
        categories = categories.order_by ('restricted')
        cat = int( category_selected )
        if not str( filter_key  ) == ''  :
            if posts.count() > 6 :
                posts = posts.filter(filter_key=filter_key)
            categories = Category.objects.all().filter(name=subdomain)
            category_selected = int( categories[0].pk )
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
            visit , _  = Visit.objects.update_or_create(visitor=visitor,post=post)
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
            "comment_author" : visitor,
            "post_author" : visitor, 
            "author_type" : author_type,
            "author_type_display" : author_type_display,
            "is_staff" : is_staff,
            "username" : username,
            "selected" : pk,
            "selected_posts" : selected_posts,
            "comments" : comments,
            "filter_key" : filter_key,
            "referer" : referer,
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
#@xframe_options_exempt  # N
def blog_add_post(request ):
    username = request.session.get('username',None)
    is_authenticated = request.session.get('is_authenticated',False)
    if not is_authenticated :
        raise PermissionDenied("You must be authenticated in to add a post")
        
    subdomain = request.session.get('subdomain','default')
    post_author = Visitor.objects.get(name=username,subdomain__name=subdomain)
    try :
        category_ = request.POST.get('category')[0]
        category = Category.objects.get(pk=category_)
    except ObjectDoesNotExist as e :
        category = Category.objects.all()[0]
    filter_key , _ = FilterKey.objects.get_or_create( name='ABCDEFG')
    post, _  = Post.objects.get_or_create(title='',body='',post_author=post_author, category=category)
    post.filter_key.clear()
    post.filter_key.add(filter_key)
    post.save()
    if request.method == "POST":
        is_staff = request.session.get('is_staff',False)
        form = PostForm( request.POST, is_staff=is_staff, instance=post )
        if form.is_valid() :
            form.save()  # S
            form.save()
            return HttpResponseRedirect(f'/edit_post/{post.pk}')
        else :
            pass
    else :
        form = PostForm( is_staff=is_staff, instance=post)
    r = render(request, "blog/blog_edit_post.html", {'form' : form, 'is_staff' : is_staff  } )
    return r


@api_view(["GET", "POST"])
#@xframe_options_exempt  # N
def blog_delete_post(request, pk ):
    if not request.session.get('is_authenticated',False ):
        raise PermissionDenied("You must be authenticated in to edit a post")
    post = get_object_or_404(Post, pk=pk)
    username = request.session.get('username',None)
    category_selected = post.category.pk
    post.delete();
    return HttpResponseRedirect(f'/blog/{category_selected}')




@api_view(["GET", "POST"])
#@xframe_options_exempt  # N
def blog_edit_post(request, pk ):
    if not request.session.get('is_authenticated',False ):
        raise PermissionDenied("You must be authenticated in to edit a post")
    action = request.POST.get('action','edit');
    post = get_object_or_404(Post, pk=pk)
    username = request.session.get('username',None)
    subdomain = request.session.get('subdomain','default')
    visitor = Visitor.objects.get(name=username,subdomain__name=subdomain)
    post.post_author = visitor
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
        return render(request, "blog/blog_edit_post.html", {'form' : form, 'is_staff' : is_staff , 'newfield' : 'NEWFIELD' } )




@api_view(["GET", "POST"])
#@xframe_options_exempt  # N
def blog_leave_comment (request, pk):

    post = Post.objects.get(pk=pk)
    post_pk = pk
    username = get_username(request) 
    subdomain = request.session.get('subdomain','default')
    comment_author = Visitor.objects.get(name=username,subdomain__name=subdomain)
    body = ''
    comment , _ = Comment.objects.get_or_create(comment_author=comment_author,post=post,body=body)
    if request.method == "POST":
        form = CommentForm( request.POST, instance=comment)
        if form.is_valid() and form.instance.body != '' and form.instance.comment_author != '':
            form.save()  # S
            form.save()
            return HttpResponseRedirect(f'/post/{comment.post.pk}')
        else :
            pass
    else :
        form = CommentForm( instance=comment)
    return render(request, "blog/blog_edit_comment.html", {'form' : form, 'username' : username   } )




@api_view(["GET", "POST"])
#@xframe_options_exempt  # N
def blog_edit_comment(request, pk ):
    comment = get_object_or_404(Comment, pk=pk)
    username = get_username(request)
    subdomain = request.session.get('subdomain','default')
    comment_author = Visitor.objects.get(name=username,subdomain__name=subdomain)
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
#@xframe_options_exempt  # N
def blog_delete_comment(request, pk ):
    comment = get_object_or_404(Comment, pk=pk)
    username = request.user.username
    action = request.POST.get('action','edit');
    post = comment.post
    comment.delete();
    return HttpResponseRedirect(f'/post/{post.pk}')

