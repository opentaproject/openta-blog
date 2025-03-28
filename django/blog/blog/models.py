from django.db import models 
from django_ckeditor_5.fields import CKEditor5Field
from django.contrib.auth.models import User
from django.views.generic.edit import UpdateView, CreateView
from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings
import re
from django.urls import reverse_lazy
from django.db.models import Count, Subquery, Sum, OuterRef, F

PRIVATE = 1 # ONLY SEEN BY TEACHER,STAFF AND OWNER
PUBLIC = 2  # SEEN BY EVERYONE 
ANONYMOUS = 0 # ANYONE ; CANNOT ADD POST
STUDENT = 1   # COMES VIA LTI  AS STUDENT
TEACHER = 2   # COMES VIA LTI  WITH ESCALATED ROLE
STAFF = 3     # 


class Subdomain( models.Model) :
    name = models.CharField(max_length=60)

    def __str__(self):
        return self.name

    def get_filterkeys_with_posts(self):
        category ,_ = Category.objects.get_or_create(name=self.name, restricted=True,hidden=False, subdomain=self  )
        posts = Post.objects.all().filter(category=category)
        f = list( FilterKey.objects.all().filter(id__in=posts.values('filter_key')\
            .distinct() ).values_list('name',flat=True) )
        f = [i for i in f if re.match(r"^\w{8}-\w{4}-\w{4}-\w{4}-\w{12}",i) ]
        return  f
 


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

    def get_resolvable_posts(self):
        my_posts =  Post.objects.filter(post_author=self)
        p = list( Comment.objects.filter(comment_author=self).values_list('post',flat=True) )
        my_commented_posts = Post.objects.filter(pk__in=p )
        resolvable = my_posts | my_commented_posts
        return resolvable

    def get_unread_filtertypes(self):
        pks = Visit.objects.all().filter(visitor=self).values('post_id')
        subdomain = self.subdomain
        categories = Category.objects.filter(name=subdomain) | Category.objects.filter(restricted=False)
        posts = Post.objects.filter(category__in=categories)
        if pks :
            first_visit =  Visit.objects.all().filter(visitor=self).order_by('date').first()
            last_visit =  Visit.objects.all().filter(visitor=self).order_by('date').last()
            visit_date = last_visit.date
            new_posts =  posts.filter(last_modified__gt=last_visit.date)
            unvisited_posts = posts.exclude(pk__in=pks)
            posts = new_posts | unvisited_posts
        fk = list( posts.values_list('filter_key__name', flat=True) )
        return  fk


        



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
    post_author =  models.ForeignKey("Visitor", null=True, blank=True, related_name="post",on_delete=models.SET_NULL)
    title = models.CharField(max_length=255)
    body = CKEditor5Field('Post Body ', config_name='extends')
    created_on = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    category = models.ForeignKey("Category", null=True, blank=True, related_name="post",on_delete=models.SET_NULL)
    filter_key = models.ManyToManyField(FilterKey,related_name="post",blank=True)
    resolved =  models.BooleanField(default=False) 

    #def save( self, *args, **kwargs):
    #    print(f"SAVE KWARGS = {kwargs}")
    #    if 'update_fields' in kwargs and kwargs['update_fields'] == ['resolved']:
    #        self._meta.get_field('last_modified').auto_now = False
    #        super().save(*args, **kwargs)
    #        self._meta.get_field('last_modified').auto_now = True
    #    else:
    #    super().save(*args, **kwargs)

    def answered_by(self):
        f = ['','s','i','a']
        answered_by = [ f"<span class='OpenTA-author-type-{i}'> {f[i]} </span>"  for i in list( set( list( self.comment.all().values_list('comment_author__visitor_type',flat=True) )  ) ) ]
        return ''.join(answered_by)

    def get_filterkeys( self ):
        filter_keys = self.filter_key
        f = list( filter_keys.values_list('title',flat=True) )
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
        try :
            k = self.post_author.visitor_type
        except :
            k = 0
        colors = ['px-2 bg-white','px-2 bg-green-400','px-2 bg-yellow-400','px-2 red-400']
        return colors[ k ]

    def tx(self):
        try :
            k = self.post_author.visitor_type
        except :
            k = 0
        c = ['','s','i','a']
        return c[k]



    def textclass(self ):
        colors = ['text-green-800','text-gray-600','text-blue-600','text-blue-600']
        try : 
            k =  self.author_type 
        except:
            k = 0
        return colors[ k ]


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


    def bgclass(self ):
        colors = ['px-2 bg-white','px-2 bg-green-400','px-2 bg-yellow-400','px-2 red-400']
        return colors[ self.comment_author.visitor_type]

    def tx(self):
        c = ['','s','i','a']
        return c[ self.comment_author.visitor_type ]


