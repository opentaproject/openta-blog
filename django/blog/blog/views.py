# blogs/views.py
from django.http import HttpResponseRedirect
from blog.models import Post, Comment, Category
from django.db import ProgrammingError
from blog.forms import CommentForm
from rest_framework.decorators import api_view
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.clickjacking import xframe_options_exempt
import logging
import json
from django.http import JsonResponse
logger = logging.getLogger(__name__)


@api_view(["GET", "POST"])
@xframe_options_exempt  # N
def blog_index(request, category_selected=1):
    logger.error(f"CATEGORY_SELECTED = {category_selected} METHOD={request.method} ")
    logger.error(f"SESSION = {request.session}")
    if request.method == 'POST' :
        data = dict( request.POST )
        username = data.get('custom_canvas_login_id', '')
        request.session['username'] = username
    else :
        print(f"GET = {request.GET}")
        username = request.GET.get('user',request.user.username)
        request.session['username'] = username
        logger.error(f"GET = {request.body}")
    logger.error(f"SESSION USERNAME = {request.session.get('username',None)}")


    logger.error(f"USER = {username}")
    try :
        posts = Post.objects.all().order_by("-created_on").filter(categories__pk=category_selected)
        logger.error(f"POSTS = {posts}")
        categories = Category.objects.all()
        cat = int( category_selected )



        is_authenticated = not( username == ''  )
        logger.error(f" USER = {username} IS_AUTHENTICATED = {is_authenticated}")
        for post in posts :
            comments = Comment.objects.filter(post=post)
            post.comments = comments


        context = {
            "posts": posts,
            "categories":  categories,
            "category_selected" : cat,
            "is_authenticated" : is_authenticated,
            "username" : request.user.username,
        }
    except ProgrammingError as e:
        context = {
            "posts" : [],
            "categoies" : [],
            "category_selected" : None
            }
        logger.error(f"ERROR = {type(e).__name__} {str(e)}")
    return render(request, "blog/sidebyside.html", context)

def blog_category(request, category):
    posts = Post.objects.filter(
        categories__name__contains=category
    ).order_by("-created_on")
    context = {
        "category": category,
        "posts": posts,
    }
    return render(request, "blog/category.html", context)




@api_view(["GET", "POST"])
@xframe_options_exempt  # N
def blog_leave_comment(request, pk):
    post = Post.objects.get(pk=pk)
    form = CommentForm()
    categories = Category.objects.all()
    if request.method == "POST":
        form = CommentForm(request.POST)
        #if request.user.is_authenticated :
        #    user = request.user
        #else :
        #    user = None
        user = request.session.get('username',None)
        if form.is_valid():
            comment = Comment(
                author=form.cleaned_data["author"],
                body=form.cleaned_data["body"],
                post=post,
                username=request.user.username,
            )
            comment.save()
            print(f"REDIRECTR TO {request.path_info}")
            return HttpResponseRedirect(f'/blog/{post.pk}')
    
    comments = Comment.objects.filter(post=post)
    cat =  post.categories.pk
    print(f"CAT = {cat}")
    user = request.session.get('username',None)
    print(f"FORM2 = {form}")
    context = {
        "post": post,
        "comments": comments,
        "form": CommentForm(),
        "author" : user,
        "categories" : categories,
        "category_selected" : cat,
        "username" : request.user.username,

        
    }
    return render(request, "blog/blog_leave_comment.html", context)

@api_view(["GET", "POST"])
@xframe_options_exempt  # N
def blog_edit_comment(request, pk):
    print(f"EDIT_COMMENT")
    comment = get_object_or_404(Comment, pk=pk)
    username = request.user.username
    print(f"AUTHOR = {comment.author}")
    print(f"BODY = {comment.body}")
    print(f"CREATED_ON = {comment.created_on}")
    print(f"post = {comment.post}")
    post = comment.post
    print(f"USER = {username} AUTHOR = {comment.author}")

    if request.method == "POST":
        form = CommentForm( request.POST, instance=comment)
        if form.is_valid():
            form.save()  # S
            form.save()
            return HttpResponseRedirect(f'/comment/{comment.pk}')
        else :
            print(f"FORM IS NOT VALID ")
    else :
        form = CommentForm( instance=comment)
    return render(request, "blog/blog_edit_comment.html", {'form' : form, 'username' : request.user.username   } )
