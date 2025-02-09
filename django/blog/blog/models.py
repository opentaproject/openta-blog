from django.db import models 
from django_ckeditor_5.fields import CKEditor5Field
from django.contrib.auth.models import User
from django.views.generic.edit import UpdateView, CreateView
from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings
import re
from django.urls import reverse_lazy
from django.db.models import Count, Subquery, Sum, OuterRef, F


class Subdomain( models.Model) :
    name = models.CharField(max_length=60)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=30)
    restricted = models.BooleanField(default=False) # ONLY SEEN BY THOSE IN SAME SUBDOMAIN
    hidden = models.BooleanField(default=False,) # ONLY SEEN BY STAFF
    subdomain = models.ForeignKey(Subdomain, on_delete=models.CASCADE, null=True, blank=True,  related_name="category")
    class Meta:
        verbose_name_plural = "category"

    def __str__(self):
        return self.name

    def get_filterkeys( self ):
        posts = Post.objects.all().filter(category=self)
        filter_keys_with_posts = list( FilterKey.objects.all().filter(id__in=posts.values('filter_key').distinct() ).values('title','name') )
        filter_keys = FilterKey.objects.all().filter(category=self)
        f = list( filter_keys.values_list('name',flat=True) )
        f = [i for i in f if re.match(r"^\w{8}-\w{4}-\w{4}-\w{4}-\w{12}",i) ] # THIS EXCLUDES THE AUTOMATICALLY GENERATED KEYS OF EXERCISES
        if settings.HIDE_UUID :
            filter_keys = filter_keys.exclude(name__in=f)

        return filter_keys

    def get_posts( self ):
        posts = Post.objects.all().filter(category=self)
        return posts


class FilterKey(models.Model):

    name = models.CharField(max_length=120)
    title = models.TextField(blank=True, default='')
    #subdomain = models.ForeignKey(Subdomain, on_delete=models.CASCADE, null=True, blank=True,  related_name="filterkey")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True,  related_name="filterkey")

    def __str__(self):
        return f"{self.title}" # -[ {self.category}:{self.name} ]" # UID

    def get_posts( self ):
        posts = self.post.all()
        posts = posts.filter(category=self.category)
        v = list( posts.values_list("pk",flat=True) )
        #p = ",".join(v)
        #print(f"P = {p}")
        return  v





class Visitor(models.Model) :

    class VisitorType( models.IntegerChoices ):

        ANONYMOUS = 0 # ANYONE ; CANNOT ADD POST
        STUDENT = 1   # COMES VIA LTI  AS STUDENT
        TEACHER = 2   # COMES VIA LTI  WITH ESCALATED ROLE
        STAFF = 3     # IS LEGITIMATE STAFF OF SIDECAR; HAS NOTHING TO DO WITH ROLE ON OPENTA

    name = models.CharField(max_length=120)
    subdomain = models.ForeignKey("Subdomain", on_delete=models.CASCADE,null=True, blank=True,  related_name="visitor")
    last_visit =  models.DateTimeField(auto_now=True)
    visitor_type =  models.IntegerField(choices=VisitorType, default=0 )
    alias = models.CharField(max_length=120,blank=True, default='')

    def __str__(self):
        return self.name+'@'+f"{self.subdomain}"

    def visitor_type_name(self):
        names = ['anonymous','student','teacher','staff']
        return names[ self.visitor_type ]



class Visit(models.Model) :
    visitor = models.ForeignKey("Visitor", on_delete=models.CASCADE, related_name="visit_visitor")
    post = models.ForeignKey("Post", on_delete=models.CASCADE, related_name="visit_post")
    date =  models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{ self.visitor}-{self.post.title}"



class Post(models.Model):
    class Visibility( models.IntegerChoices ):
        PRIVATE = 1 # ONLY SEEN BY TEACHER,STAFF AND OWNER
        PUBLIC = 2  # SEEN BY EVERYONE 
    class AuthorType( models.IntegerChoices ):
        ANONYMOUS = 0 # ANYONE ; CANNOT ADD POST
        STUDENT = 1   # COMES VIA LTI  AS STUDENT
        TEACHER = 2   # COMES VIA LTI  WITH ESCALATED ROLE
        STAFF = 3     # IS LEGITIMATE STAFF OF SIDECAR; HAS NOTHING TO DO WITH ROLE ON OPENTA
    visibility = models.IntegerField(choices=Visibility , default=2 )
    author_type = models.IntegerField(choices=AuthorType, default=0 )
    #author = models.CharField(max_length=60)
    post_author =  models.ForeignKey("Visitor", null=True, blank=True, related_name="post",on_delete=models.SET_NULL)
    title = models.CharField(max_length=255)
    body = CKEditor5Field('Post Body ', config_name='extends')
    created_on = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    category = models.ForeignKey("Category", null=True, blank=True, related_name="post",on_delete=models.SET_NULL)
    filter_key = models.ManyToManyField(FilterKey,related_name="post")

    def save( self, *args, **kwargs):
        super().save(*args,**kwargs)

    def answered_by(self):
        f = ['A','S','I','Admin']
        answered_by = [ f"<span class='OpenTA-author-type-{i}'> {f[i]} </span>"  for i in list( set( list( self.comment.all().values_list('comment_author__visitor_type',flat=True) )  ) ) ]
        return ','.join(answered_by)

    def get_filterkeys( self ):
        filter_keys = self.filter_key
        f = list( filter_keys.values_list('name',flat=True) )
        #f = [i for i in f if re.match(r"^\w{8}-\w{4}-\w{4}-\w{4}-\w{12}",i) ] # THIS EXCLUDES THE AUTOMATICALLY GENERATED KEYS OF EXERCISES
        return f


    def __str__(self):
        return self.title


    def tot_visits(self ):
        v = Visit.objects.filter(post=self).count()
        return v

    def visits(self,username) :
        v = Visit.objects.filter(visitor=username,post=self, post__last_modified__lt=F('date') ).count()
        #print(f"V = {v}")
        return v

    def bgclass(self ):
        colors = ['bg-green-200','bg-gray-400','bg-blue-400','bg-bule-400']
        return colors[ self.author_type ]

    def textclass(self ):
        colors = ['text-green-800','text-gray-600','text-blue-600','text-blue-600']
        return colors[ self.author_type ]


class Comment(models.Model):
    #author = models.CharField(max_length=60,default='',blank=True)
    comment_author =  models.ForeignKey("Visitor", null=True, blank=True, related_name="comment_author",on_delete=models.SET_NULL)
    body =   CKEditor5Field('Comment Body', config_name='extends')
    created_on = models.DateTimeField(auto_now_add=True)
    post = models.ForeignKey("Post", on_delete=models.CASCADE,related_name="comment")

    def __str__(self):
        return f"{self.comment_author} on '{self.post}'"

    def save( self, *args, **kwargs ):
        post = self.post
        post.save() 
        super().save(*args,**kwargs)
