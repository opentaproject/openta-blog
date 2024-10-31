# blogs/views.py
from django.shortcuts import render
from django.http import HttpResponseRedirect
from blog.models import Post, Comment, Category
from django.db import ProgrammingError
from blog.forms import CommentForm


def blog_index(request, category_selected=1):
    print(f"CATEGORY_SELECTED = {category_selected}")
    try :
        posts = Post.objects.all().order_by("-created_on").filter(categories__pk=category_selected)
        print(f"POSTS = {posts}")
        categories = Category.objects.all()
        cat = int( category_selected )
        for post in posts :
            comments = Comment.objects.filter(post=post)
            post.comments = comments
        context = {
            "posts": posts,
            "categories":  categories,
            "category_selected" : cat,
        }
    except ProgrammingError as e:
        context = {
            "posts" : [],
            "categoies" : [],
            "category_selected" : None
            }
        print(f"ERROR = {type(e).__name__} {str(e)}")
    return render(request, "blog/index.html", context)

def blog_category(request, category):
    posts = Post.objects.filter(
        categories__name__contains=category
    ).order_by("-created_on")
    context = {
        "category": category,
        "posts": posts,
    }
    return render(request, "blog/category.html", context)


def blog_leave_comment(request, pk):
    post = Post.objects.get(pk=pk)
    form = CommentForm()
    categories = Category.objects.all()
    if request.method == "POST":
        form = CommentForm(request.POST)
        if request.user.is_authenticated :
            user = request.user
        else :
            user = None
        if form.is_valid():
            comment = Comment(
                author=form.cleaned_data["author"],
                body=form.cleaned_data["body"],
                post=post,
                user=user,
            )
            comment.save()
            print(f"REDIRECTR TO {request.path_info}")
            return HttpResponseRedirect(f'/blog/{post.pk}')
    
    comments = Comment.objects.filter(post=post)
    cat =  post.categories.pk
    print(f"CAT = {cat}")
    context = {
        "post": post,
        "comments": comments,
        "form": CommentForm(),
        "user" : request.user,
        "author" : request.user.username,
        "categories" : categories,
        "category_selected" : cat,

        
    }

    return render(request, "blog/blog_leave_comment.html", context)
