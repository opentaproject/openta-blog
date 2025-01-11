from django.db import models
from django_ckeditor_5.fields import CKEditor5Field
from django.contrib.auth.models import User
from django.views.generic.edit import UpdateView, CreateView
from django.shortcuts import render, get_object_or_404, redirect



class Category(models.Model):
    name = models.CharField(max_length=30)
    restricted = models.BooleanField(default=False)
    hidden = models.BooleanField(default=False,)
    class Meta:
        verbose_name_plural = "category"

    def __str__(self):
        return self.name
    
from django.urls import reverse_lazy

class Visitor(models.Model) :

    class VisitorType( models.IntegerChoices ):
        ANONYMOUS = 0
        STUDENT = 1
        TEACHER = 2
        STAFF = 3

    name = models.CharField(max_length=60)
    subdomain = models.ForeignKey("Subdomain", on_delete=models.CASCADE,null=True, blank=True,  related_name="visitor")
    last_visit =  models.DateTimeField(auto_now=True)
    visitor_type =  models.IntegerField(choices=VisitorType, default=0 )


    def __str__(self):
        return self.name


class Subdomain( models.Model) :
    name = models.CharField(max_length=60)

    def __str__(self):
        return self.name


class Visit(models.Model) :
    visitor = models.CharField(max_length=60)
    post = models.ForeignKey("Post", on_delete=models.CASCADE, related_name="visit")
    date =  models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{ self.visitor.name}-{self.post.title}"



class Post(models.Model):
    class Visibility( models.IntegerChoices ):
        PRIVATE = 1
        PUBLIC = 2 
    class AuthorType( models.IntegerChoices ):
        ANONYMOUS = 0
        STUDENT = 1
        TEACHER = 2
        STAFF = 3
    visibility = models.IntegerField(choices=Visibility , default=2 )
    author_type = models.IntegerField(choices=AuthorType, default=0 )
    author = models.CharField(max_length=60)
    post_author =  models.ForeignKey("Visitor", null=True, blank=True, related_name="post",on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    body = CKEditor5Field('Text', config_name='extends')
    created_on = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    category = models.ForeignKey("Category", null=True, blank=True, related_name="post",on_delete=models.CASCADE)

    def __str__(self):
        return self.title


    def tot_visits(self ):
        v = Visit.objects.filter(post=self).count()
        return v

    def visits(self,username) :
        v = Visit.objects.filter(visitor=username,post=self, post__last_modified__lt=F('date') ).count()
        print(f"V = {v}")
        return v

    def bgclass(self ):
        colors = ['bg-green-200','bg-gray-400','bg-blue-400','bg-bule-400']
        return colors[ self.author_type ]

    def textclass(self ):
        colors = ['text-green-800','text-gray-600','text-blue-600','text-blue-600']
        return colors[ self.author_type ]


class Comment(models.Model):
    author = models.CharField(max_length=60,default='',blank=True)
    body =   CKEditor5Field('Text', config_name='extends')
    created_on = models.DateTimeField(auto_now_add=True)
    post = models.ForeignKey("Post", on_delete=models.CASCADE,related_name="comment")

    def __str__(self):
        return f"{self.author} on '{self.post}'"

    def save( self, *args, **kwargs ):
        post = self.post
        post.save() 
        super().save(*args,**kwargs)



class CommentUpdateView(UpdateView):
    model = Comment
    fields = ['body', 'category','title']

    def get_success_url(self)  :
        url = f'/post/{self.post.pk}'
        print(f"REDIRECT TO {url}")
        return redirect(url)

class CommentCreateView(CreateView):
    model = Comment
    fields = ['body', 'category','title']

    def get_success_url(self)  :
        print(f"CREATE_VIEW_SUCCESS_URL")
        url = f'/post/{self.post.pk}'
        print(f"REDIRECT TO {url}")
        return redirect(url)
