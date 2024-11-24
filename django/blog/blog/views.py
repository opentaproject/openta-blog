# blogs/views.py
from django.http import HttpResponseRedirect
from blog.models import Post, Comment, Category
from django.db import ProgrammingError
from blog.forms import CommentForm, PostForm
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
        categories = Category.objects.all()
        cat = int( category_selected )



        is_authenticated = not( username == ''  )
        logger.error(f" USER = {username} IS_AUTHENTICATED = {is_authenticated}")
        for post in posts :
            comments = Comment.objects.filter(post=post ).order_by('-created_on')
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
def blog_add_post(request ):
    username = request.user.username
    author = username
    body = '<p> Initial content </p> '
    title = 'Title'
    categories = Category.objects.all()[0]
    post, _  = Post.objects.get_or_create(categories=categories,title=title,body=body)
    print(f"ADD_POST {post.pk}")
    if request.method == "POST":
        form = PostForm( request.POST, instance=post)
        print(f"SAVING POST {post.pk}")
        if form.is_valid():
            form.save()  # S
            form.save()
            return HttpResponseRedirect(f'/edit_post/{post.pk}')
        else :
            print(f"POST FORM IS NOT VALID ")
    else :
        form = PostForm( instance=post)
    return render(request, "blog/blog_edit_post.html", {'form' : form, 'username' : username  } )


@api_view(["GET", "POST"])
@xframe_options_exempt  # N
def blog_edit_post(request, pk):
    print(f"EDIT_POST PK={pk}")
    post = get_object_or_404(Post, pk=pk)
    username = request.user.username
    print(f"BODY = {post.body}")
    print(f"post = {post.pk}")

    if request.method == "POST":
        form = PostForm( request.POST, instance=post)
        if form.is_valid():
            form.save()  # S
            form.save()
            print(f"SAVING POST {post.pk}")
            return HttpResponseRedirect(f'/edit_post/{post.pk}')
        else :
            print(f"FORM IS NOT VALID ")
    else :
        form = PostForm( instance=post)
    return render(request, "blog/blog_edit_post.html", {'form' : form, 'username' : request.user.username   } )




@api_view(["GET", "POST"])
@xframe_options_exempt  # N
def blog_leave_comment (request, pk):

    post = Post.objects.get(pk=pk)
    post_pk = pk
    print(f"LEAVE_COMMENT")
    username = request.user.username
    author = username
    body = 'Initial content'
    comment = Comment.objects.create(author=author,post=post )
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
