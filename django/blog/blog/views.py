# blogs/views.py
from django.db.models import Count, Subquery, Sum, OuterRef, F
import hmac
import json
import re
import hashlib
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect, HttpResponse
from blog.models import Post, Comment, Category,Visit,Visitor,Subdomain, FilterKey
from django.db import ProgrammingError
from blog.forms import CommentForm, PostForm
from rest_framework.decorators import api_view
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseForbidden
from django.views.decorators.clickjacking import xframe_options_exempt
import time, base64
import logging
from django.http import JsonResponse
from oauthlib.oauth1 import RequestValidator
logger = logging.getLogger(__name__)
from oauthlib.oauth1 import RequestValidator
from backend.oauth1 import load_session_variables, get_author_type, get_username
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from .forms import CategoryForm, FilterKeyForm

ANONYMOUS = 0
STUDENT = 1
TEACHER = 2
STAFF = 3

PRIVATE = 1
PUBLIC = 2 

def get_visitor( request ):
    subdomain_name = request.session.get('subdomain','')
    username = request.session['username']
    subdomain, _ = Subdomain.objects.get_or_create(name=subdomain_name)
    visitor_type = get_author_type(request)
    visitor, _ = Visitor.objects.update_or_create(name=username,subdomain=subdomain,visitor_type=visitor_type)
    return visitor


@api_view(["GET", "POST"])
#@csrf_exempt
#@xframe_options_exempt  
def toggle_resolved(request, *args, **kwargs ) :
    val = kwargs.get('val') == 'True'
    pk = kwargs.get('pk')
    post = Post.objects.get(pk=pk)
    post.resolved = not post.resolved
    post.save(update_fields=['resolved'])
    if post.resolved  :
        #ret = '<i class="fas fa-toggle-on fa-2x"> </i> '
        ret = 'Resolved'
    else :
        ret = 'Unresolved' # '<i class="fas fa-toggle-off fa-2x"> </i> '
    return HttpResponse(ret)




@api_view(["GET", "POST"])
@csrf_exempt
@xframe_options_exempt  
def sidecar_count(request, *args, **kwargs ) :


    username = request.POST.get('username','')
    subdomain = request.POST.get('subdomain','')
    subdomain_ ,_ = Subdomain.objects.get_or_create(name=subdomain)
    exercises_with_posts = subdomain_.get_filterkeys_with_posts() 
    exercise = str( request.POST.get('exercise') )
    visitor = Visitor.objects.filter(name=username,subdomain__name=subdomain).order_by('-last_visit')
    pks = Visit.objects.all().filter(visitor__in=visitor).values('post_id')
    #if False and len( pks ) == 0 :
    #    unread = []
    #    sidecar_count = 0 
    unread =  visitor[0].get_unread_filtertypes()
    print(f"UNREAD = {unread}")
    sidecar_count = len( unread )
    if exercise == 'None' :
        sidecar_count = len( unread)
    else :
        filterkeys = FilterKey.objects.filter(name=exercise)
        #posts = list( Post.objects.all().filter(filter_key__in=filterkeys).values_list('pk',flat=True) )
        posts = Post.objects.all().filter(filter_key__in=filterkeys)
        visits = Visit.objects.all().filter(visitor__in=visitor,post__in=posts)
        if visits:
            first_visit =  visits.order_by('date').first().date
            last_visit =   visits.order_by('date').last().date
            new_posts =  posts.filter(last_modified__gt=last_visit)
            pks = list( visits.values_list('post__pk',flat=True) )
            unvisited_posts = posts.exclude(pk__in=pks)
            posts = new_posts | unvisited_posts
        else :
            unread = exercises_with_posts
        #visitor = models.ForeignKey("Visitor", on_delete=models.CASCADE, related_name="visit_visitor")
        #post = models.ForeignKey("Post", on_delete=models.CASCADE, related_name="visit_post")
        #date =  models.DateTimeField(auto_now=True)
        sidecar_count = len( posts)
    data = {'sidecar_count' : sidecar_count ,'unread' : unread, 'exercises_with_posts' : exercises_with_posts  }
    print(f"SIDECAR_COUNT {username} {subdomain} { exercise } { data }")
    return JsonResponse( data )


@api_view(["GET", "POST"])
@csrf_exempt
@xframe_options_exempt  
def blog_index(request, *args, **kwargs ) :
    pk = kwargs.get('pk',None)
    #category_selected = kwargs.get('category_selected',request.session.get('category_selected',None ) )
    path =  request.build_absolute_uri() 
    uri = str(  request.build_absolute_uri()  )
    if not load_session_variables( request, args, kwargs ) :
        return HttpResponseForbidden("Session Variable Load failed")
    if 'home' in uri :
        pass
        #del request.session['filter_title']  
        #del request.session['category_selected'] 
    referer =  request.session.get('referer','')
    try :
        fkey =  json.loads( request.session.get('filter_key','')  )
        names = list( fkey.keys() )
    except :
        fkey = {};
        names = []
    server = str( request.session.get('server','')  )
    subdomain_name = request.session.get('subdomain','')
    subdomain, _ = Subdomain.objects.get_or_create(name=subdomain_name)
    category_selected = request.session.get('category_selected',None)
    username = request.session['username']
    if  len( Category.objects.filter(name=subdomain_name,subdomain=subdomain)  ) == 0 :
        print(f"SUBDOMAIN_NAME = {subdomain_name}")
        new_category = Category.objects.create(name=subdomain_name,subdomain=subdomain,restricted=True)
        new_category.save() 
    filter_key = None
    for nam in names :
        title = fkey[nam]
        if  not subdomain_name == '' and not title == '' and not nam == ''  :
            category = Category.objects.get(name=subdomain_name,subdomain=subdomain)
            filter_key , _  = FilterKey.objects.get_or_create(name=nam.strip() ,category=category,title=title.strip() )
        else :
            filter_key = None


    try :
        visitor_type = get_author_type(request)
        visitor = get_visitor( request )
        if visitor.alias == ''  or '@' in visitor.alias :
            visitor.alias = visitor.name.split('@')[0];
            visitor.save()
        comments  = []

        def get_categories_and_posts( visitor, subdomain_name, category_selected , filter_key ):
            if subdomain_name != '' :
                subdomain = Subdomain.objects.get(name=subdomain_name)
            else :
                subdomain = None
            category_all ,_ = Category.objects.get_or_create(name='All')
            category_unread , _  = Category.objects.get_or_create(name='Unread')
            category_unresolved, _  = Category.objects.get_or_create(name='Unresolved')
            category_mine, _  = Category.objects.get_or_create(name='Mine')
            ALL = category_all.pk
            MINE = category_mine.pk
            UNREAD = category_unread.pk
            category_selected = int( category_selected )
            UNRESOLVED = category_unresolved.pk
            if  category_selected ==  ALL :
                posts = Post.objects.all().order_by("-last_modified").annotate(viewed=Count('comment') )
            elif category_selected == UNRESOLVED :
                posts = Post.objects.filter(resolved=False).order_by("-last_modified").annotate(viewed=Count('comment') )
            elif category_selected == MINE:
                posts = visitor.get_resolvable_posts().order_by("-last_modified").annotate(viewed=Count('comment') )
            else :
                posts = Post.objects.all().order_by("-last_modified").filter(category__pk=category_selected).annotate(viewed=Count('comment') )
            for post in posts :
                if post.body == '' : ## THERE SHOULD BE BETTER WAY TO ENFORCE NONEMPTY BODY
                    post.delete()
            post_subquery = Post.objects.filter(id=OuterRef('id'),post_author=visitor).annotate(viewed=Count('post_author')).values('viewed')
            used_categories = Category.objects.filter( id__in= Post.objects.values('category').distinct() )
            visit_subquery = Visit.objects.filter(post=OuterRef('id'),visitor=visitor,  post__last_modified__lt=F('date') ).annotate(viewed=Count('visitor') ).values('viewed')
            if category_selected ==  ALL :
                posts = Post.objects.all().order_by("-last_modified").annotate(viewed=Subquery(visit_subquery)  )
            elif category_selected ==  UNREAD :
                cat1 = Category.objects.filter( restricted=False)
                if get_author_type(request) >= STUDENT :
                    cat2 = Category.objects.filter( subdomain__name=subdomain,name=subdomain,restricted=True)
                    cat  = cat1 | cat2 
                else :
                    cat = cat1
                posts =  Post.objects.filter(category__in=cat)
                pks = Visit.objects.all().filter(visitor=visitor).values('post_id')
                if pks :
                    first_visit =  Visit.objects.all().filter(visitor=visitor).order_by('date').first()
                    last_visit =  Visit.objects.all().filter(visitor=visitor).order_by('date').last()
                    visit_date = last_visit.date
                    new_posts =  posts.filter(last_modified__gt=last_visit.date)
                    unvisited_posts = posts.exclude(pk__in=pks)
                    posts = new_posts | unvisited_posts
            elif category_selected == UNRESOLVED:
                posts = Post.objects.filter(resolved=False).order_by("-last_modified").annotate(viewed=Subquery(visit_subquery)  )
            elif category_selected == MINE :
                posts = visitor.get_resolvable_posts().order_by("-last_modified").annotate(viewed=Subquery(visit_subquery)  )
            else :
                posts = Post.objects.all().order_by("-last_modified").filter(category__pk=category_selected).annotate(viewed=Subquery(visit_subquery)  )
            if visitor.visitor_type in [ ANONYMOUS , STUDENT ] :
                posts_visible = posts.filter(visibility=PUBLIC)
                posts_own     = posts.filter(post_author=visitor)
                posts = posts_visible | posts_own 
            if request.session['is_staff']  :
                closed = used_categories
                copen = Category.objects.all().filter(restricted=False,hidden=False)
                categories = ( closed | copen )
            else :
                copen = Category.objects.all().filter(restricted=False,hidden=False)
                if subdomain :
                    closed = Category.objects.all().filter(restricted=True,subdomain=subdomain,hidden=False)
                    categories = ( closed | copen )
                else :
                    categories = copen
            #for c in categories :
            #    f = c.get_filterkeys()
            #    print(f" C={c} F = {f}")
            first_list = ['All','Unread']
            last_categories = categories.exclude(name__in=first_list).order_by('name')
            first_categories = categories.filter(name__in=first_list).order_by('name')
            categories = (first_categories | last_categories).distinct() 
            if filter_key and subdomain_name != '' :
                subdomain = Subdomain.objects.get(name=subdomain_name)
                categories = categories.filter(subdomain=subdomain)
            cat = int( category_selected )
            posts = posts.filter(category__in=categories)
            if  filter_key and re.match(r"^\w{8}-\w{4}-\w{4}-\w{4}-\w{12}" , str( filter_key.name) ) : # and posts.count() > 0 :
                posts = posts.filter(filter_key=filter_key)
            is_teacher = visitor_type in [ TEACHER , STAFF ]
            if is_teacher :
                resolvable = list( posts.values_list('pk',flat=True) );
            elif visitor_type == STUDENT :
                p = visitor.get_resolvable_posts() 
                resolvable = list( p.values_list('pk',flat=True) );

            else :
                resolvable = []
            return ( categories , cat , posts , resolvable)
        categories, cat,  posts , resolvable = get_categories_and_posts( visitor, subdomain_name, category_selected , filter_key  )
        is_authenticated = request.session.get('is_authenticated',False)
        is_staff = request.session.get('is_staff',False)
        is_teacher = visitor_type in [ TEACHER , STAFF ]


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
            comments = Comment.objects.filter(post=post ).order_by('created_on')
            #if settings.HIDE_UUID :
            #    fk = post.filter_key.exclude(name__iregex=r"^\w{8}-\w{4}-\w{4}-\w{4}-\w{12}")
            #    post.filter_key.set(fk)
        author_type = request.session.get('author_type', Post.AuthorType.ANONYMOUS )
        author_type_display = request.session.get('author_type_display','Anonymous')
        course_pk = request.session.get("course_pk")
        if request.user.is_staff :
            author_type = Post.AuthorType.STAFF
            author_type_display = 'Admin'
        visitor_types = ['anon','student','teacher','staff']
        category_selected_name = Category.objects.get( pk=cat ).name
        if request.method == 'POST'  or 'filterkeys' not in request.COOKIES :
            filterkeys = [];
        else :
            filterkeys = [ int( i.replace('id_filterkey_','') ) for i in json.loads( request.COOKIES.get('filterkeys','')  ) if i != 'All']
        context = {
            "posts": posts,
            "categories":  categories,
            "subdomain" : subdomain_name, 
            "category_selected" : cat,
            "category_selected_name" : category_selected_name,
            "category_name_forbidden" : ['Unread','All'] , 
            "is_authenticated" : is_authenticated,
            "visibility" : Post.Visibility.PUBLIC , 
            "comment_author" : visitor,
            "post_author" : visitor, 
            "author_type" : author_type,
            "author_type_display" : author_type_display,
            "is_staff" : is_staff,
            "is_teacher" : is_teacher,
            "username" : username,
            "selected" : pk,
            "selected_posts" : selected_posts,
            "comments" : comments,
            "filter_key" : filter_key,
            "referer" : referer,
            "alias" : visitor.alias,
            "server" : server,
            "dummy_field" : 'VIEWS_DUMMY_FIELD',
            "visitor_types" : visitor_types,
            "filterkeys" : filterkeys,
            "course_pk" : course_pk,
            "resolvable" : resolvable,
        }
    except ProgrammingError as e:
        context = {
            "posts" : [],
            "categories" : [],
            "category_selected" : None
            }
        logger.error(f"ERROR = {type(e).__name__} {str(e)}")
    request.session['last_post_pk'] = pk

    return render(request, "blog/sidebyside.html", context)

#def blog_category(request, category):
#    posts = Post.objects.filter( category__name__contains=category).order_by("-created_on")
#    context = {
#        "category": category,
#        "posts": posts,
#    }
#    return render(request, "blog/category.html", context)


@api_view(["GET", "POST"])
#@xframe_options_exempt  # N
def blog_add_post(request ):
    username = request.session.get('username',None)
    filter_keys = json.loads( request.session.get('filter_key',{'':''} ) )
    is_authenticated = request.session.get('is_authenticated',False)
    if not is_authenticated :
        raise PermissionDenied("You must be authenticated in to add a post")
        
    subdomain_name = request.session.get('subdomain','')
    subdomain,_ = Subdomain.objects.get_or_create(name=subdomain_name)
    visitor_type = get_author_type(request)
    #post_author = Visitor.objects.get(name=username,subdomain=subdomain,visitor_type=visitor_type)
    post_author = get_visitor( request )
    try :
        category_ = request.POST.get('category')[0]
        category = Category.objects.get(pk=category_)
    except ObjectDoesNotExist as e :
        category = Category.objects.all()[0]
    post, _  = Post.objects.get_or_create(title='',body='',post_author=post_author, category=category)
    if category.name == subdomain.name :
        for k in filter_keys :
            filter_key_name = k;
            filter_key_title = filter_keys[k]
            if not filter_key_name == ''  :
                filter_key , _ = FilterKey.objects.get_or_create(category=category, name=filter_key_name,title=filter_key_title)
                post.filter_key.add(filter_key)
    post.save()
    alias = post.post_author.alias
    if request.method == "POST":
        is_staff = request.session.get('is_staff',False)
        instance = post
        instance.alias = alias
        qm = request.POST.copy();
        qm_selected = qm.get('filter_key_selected',None)
        try :
            if qm_selected :
                f = qm.getlist('filter_key')
                k = [  int( i.split('_')[2])  for i in  qm_selected.split(',')  ]
                f = f + k 
                qm.setlist('filter_key', f )
        except IndexError as e :
            pass
        form = PostForm( qm , is_staff=is_staff, alias=alias, instance=instance )
        if form.is_valid() :
            form.save()  # S
            form.save()
            return HttpResponseRedirect(f'/edit_post/{post.pk}')
        else :
            pass
    else :
        form = PostForm( is_staff=is_staff,alias=alias, instance=post)
    r = render(request, "blog/blog_edit_post.html", {'form' : form, 'is_staff' : is_staff , 'alias' : alias , 'dummy_field' : 'FROM_ADD_POST' } )
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
    subdomain = request.session.get('subdomain','')
    #visitor = Visitor.objects.get(name=username,subdomain__name=subdomain)
    visitor = get_visitor( request )
    alias = visitor.alias
    post.post_author = visitor
    is_staff = request.session.get('is_staff',False)
    fk = [i['pk'] for i in list( post.filter_key.all().values('pk') ) ]
    initial = {'filter_key' : fk }
    if request.method == "POST":
        if action == 'delete' :
            post.delete();
            return HttpResponseRedirect(f'/')

        form = PostForm( request.POST,  is_staff=is_staff, alias=alias ,instance=post,initial=initial)
        #if form.is_valid() and not post.body == '' :
        if  not post.body == '' :
            form.save()  # S
            form.save()
            return HttpResponseRedirect(f'/post/{post.pk}')
        else :
            pass
    else :
        form = PostForm( is_staff=is_staff, alias=alias, instance=post,initial=initial)
        r = render(request, "blog/blog_edit_post.html", {'form' : form, 'is_staff' : is_staff , 'alias' : alias , 'dummy_field' : 'FROM_EDIT_POST','initial' : initial } )

        v,_ = Visit.objects.get_or_create(visitor=visitor, post=post)
        print(f"SAVE THE VISIT {v}")
        return r




@api_view(["GET", "POST"])
#@xframe_options_exempt  # N
def blog_leave_comment (request, pk):

    post = Post.objects.get(pk=pk)
    post_pk = pk
    username = get_username(request) 
    subdomain = request.session.get('subdomain','')
    #comment_author = Visitor.objects.get(name=username,subdomain__name=subdomain)
    comment_author = get_visitor( request)
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
    subdomain = request.session.get('subdomain','')
    comment_author = get_visitor( request ) # Visitor.objects.get(name=username,subdomain__name=subdomain)
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



class FilterKeyCreateView(CreateView):
    model = FilterKey
    form_class = FilterKeyForm
    template_name = 'filter_key_form.html'
    success_url = reverse_lazy('filter_key_list')  # Redirect after successful creation

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs


# Update View
class FilterKeyUpdateView(UpdateView):
    model = FilterKey
    form_class = FilterKeyForm
    template_name = 'filter_key_form.html'
    success_url = reverse_lazy('filter_key_list')

# Delete View
class FilterKeyDeleteView(DeleteView):
    model = FilterKey
    template_name = 'filter_key_confirm_delete.html'
    success_url = reverse_lazy('filter_key_list')


class FilterKeyListView(ListView):


    model = FilterKey
    template_name = 'filter_key_list.html'
    success_url = reverse_lazy('filter_key_list')

    #def __init__(self, *args, **kwargs) :
    #    print(f"__INIT__ = {args} {kwargs} ")
    #    super().__init__(*args,**kwargs)




    def get_queryset(self, *args, **kwargs ):
        subdomain = Subdomain.objects.get(name=self.request.session.get('subdomain',''))
        categories = Category.objects.filter(subdomain=subdomain)
        filterkeys =  FilterKey.objects.filter(category__in=categories)
        f = list( filterkeys.values_list('name',flat=True) )
        f = [i for i in f if re.match(r"^\w{8}-\w{4}-\w{4}-\w{4}-\w{12}",i) ] # THIS EXCLUDES THE AUTOMATICALLY GENERATED KEYS OF EXERCISES
        if settings.HIDE_UUID :
            filterkeys = filterkeys.exclude(name__in=f)
        filterkeys = filterkeys.order_by('title')
        return filterkeys


class CategoryCreateView(CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'category_form.html'
    success_url = reverse_lazy('category_list') 

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

class CategoryListView(ListView):


    model = Category
    template_name = 'category_list.html'
    success_url = reverse_lazy('category_list')

    def __init__(self, *args, **kwargs) :
        super().__init__(*args,**kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        path = self.request.path
        subdomain_name = self.request.session.get('subdomain','')
        if not subdomain_name == '' :
            subdomain ,_ = Subdomain.objects.get_or_create(name=subdomain_name)
            queryset = queryset.filter(subdomain=subdomain)
        return queryset



class CategoryUpdateView(UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'category_form.html'
    success_url = reverse_lazy('category_list')

# Delete View
class CategoryDeleteView(DeleteView):
    model = Category
    filed = '__all__'
    template_name = 'category_confirm_delete.html'
    success_url = reverse_lazy('category_list')



