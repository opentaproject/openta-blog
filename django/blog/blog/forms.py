# blog/forms.py

from django import forms
from django.conf import settings
from django_ckeditor_5.widgets import CKEditor5Widget
from .models import Comment, Post, FilterKey, Category, Subdomain
import logging
import re
logger = logging.getLogger(__name__)
from django.forms import TextInput, Textarea



class CommentForm(forms.ModelForm):
      """Form for comments to the article."""

      def __init__(self, *args, **kwargs):
          super().__init__(*args, **kwargs)
          self.fields["body"].required = False
          self.fields["comment_author"].required = False
          self.fields['post'].widget = forms.HiddenInput();
          self.fields['comment_author'].widget = forms.HiddenInput();


      class Meta:
          model = Comment
          fields = '__all__' 
          widgets = {
              "body": CKEditor5Widget(
                  attrs={"class": "django_ckeditor_5"}, config_name="extends"
              )
          }

class PostForm(forms.ModelForm):
      """Form for posts."""

      is_staff = forms.BooleanField()
      alias = forms.CharField()

      OPTIONS = [ (1 ,'Private'),
                  (2,'Public')
                ]

      #visibility = forms.ChoiceField(
      #  choices=OPTIONS,
      #  widget=forms.RadioSelect(attrs={'class': 'inline'})
      #  )

      filter_key = forms.ModelMultipleChoiceField(
              queryset = FilterKey.objects.all(),
              widget=forms.CheckboxSelectMultiple,
              required = False 
              )
      def __init__(self,   *args, is_staff=None, alias='',  **kwargs ):
          #print(f"POST FORM kwargs = {kwargs}")
          #print(f"ALIAS IN __INIT__  = {alias}")
          instance = kwargs['instance']
          kwargs.setdefault('label_suffix', 'ABC') 
          kwargs['label_suffix'] = ''

          super().__init__(*args, **kwargs)
          #for k in self.fields.keys() :
          #    print(f" K = {k} val = {self.fields[k]}")
          self.fields["resolved"].required = False
          self.fields["body"].required = True
          self.fields["title"].required = True
          self.fields["alias"].required = False
          self.fields["alias"].initial = alias
          self.fields["post_author"].required = True
          self.fields["is_staff"].required = False
          self.fields["filter_key"].required = False
          for k in [ 'author_type', 'post_author','body','category','is_staff'] :
              self.fields[k].label = ''
          self.fields["title"].label = 'Title: '
          self.fields["visibility"].label = 'Visibility: '
          self.fields["filter_key"].label = "Folders for the post: "
          self.fields["alias"].label = 'Alias: '
          self.fields["title"].widget=forms.TextInput(attrs={'class': 'OpenTA-text-input' });
          self.fields["alias"].widget=forms.TextInput(attrs={'class': 'OpenTA-text-input',});
          self.fields["visibility"].widget = forms.RadioSelect(choices=self.OPTIONS);
          arglist = dict( *args )
          categories = arglist.get('category')
          fk = [i for i in arglist.get('filter_key',[]) if i != '' ]
          chosen_filterkeys1 = FilterKey.objects.filter(pk__in=fk )
          if kwargs.get('initial',None ):
              chosen_filterkeys2 = FilterKey.objects.filter(pk__in=kwargs.get('initial',[] ).get('filter_key',[]))
          else :
              chosen_filterkeys2 = None
          if categories == None :
            cat = instance.category
            filter_keys = FilterKey.objects.filter(category=cat)
          else :
            filter_keys = FilterKey.objects.all()
            filter_keys = filter_keys.filter(category__in=categories)
          f = list( filter_keys.values_list('name',flat=True) )
          f = [i for i in f if re.match(r"^\w{8}-\w{4}-\w{4}-\w{4}-\w{12}",i) ] # THIS EXCLUDES THE AUTOMATICALLY GENERATED KEYS OF EXERCISES
          if settings.HIDE_UUID :
            filter_keys = filter_keys.exclude(name__in=f)
          filter_keys = filter_keys | chosen_filterkeys1  
          if  chosen_filterkeys2 :
              filter_keys = filter_keys | chosen_filterkeys2

          self.fields["filter_key"].queryset = filter_keys.order_by('title')
          if True or not is_staff :
            self.fields['author_type'].widget = forms.HiddenInput({'label' : '' } );
            self.fields['category'].widget = forms.HiddenInput();
            self.is_staff = is_staff
            self.fields["is_staff"].widget = forms.HiddenInput();
            self.fields["post_author"].widget = forms.HiddenInput();
                

      def clean(self):
          cleaned_data = super().clean()
          body = cleaned_data.get('body','')
          title = cleaned_data.get('title','')
          alias = cleaned_data.get('alias','')
          post_author = cleaned_data.get('post_author')
          post_author.alias = alias
          post_author.save()
  
          if body and title:
              return cleaned_data
          else :
              raise forms.ValidationError("Title and body must be set.")
          

      class Meta:
          model = Post
          fields = ['author_type','visibility','post_author','title','body','category' ,'filter_key','alias','resolved']
          #fields = '__all__'
          error_messages = {}
          for f in fields :
              error_messages[f] = {'required' : ''  ,}

          #labels = {'post_author' : '' , 'is_staff' : '' }
          widgets = {
              "body": CKEditor5Widget( attrs={"class": "django_ckeditor_5"}, config_name="extends"),
          }
          labels = {'post_author' : '' , 'author_type' : '' }


class CategoryForm(forms.ModelForm):

    class Meta:
        model = Category
        fields = '__all__'

    def __init__(self, *args, request=None,  **kwargs):
        super().__init__(*args, **kwargs)
        instance = self.instance
        if not request == None :
            self.request = request
            subdomain_name = request.session.get('subdomain','')
            subdomain, _ = Subdomain.objects.get_or_create(name=subdomain_name)
            instance.subdomain = subdomain
            self.fields['subdomain'].initial = subdomain
        else :
            self.fields['subdomain'].initial = instance.subdomain
        self.fields['restricted'].initial  = True
        self.fields['restricted'].required = False 
        self.fields['restricted'].disabled = True
        self.fields['subdomain'].disabled = True

class FilterKeyForm(forms.ModelForm):

    class Meta:
        model = FilterKey
        fields = '__all__'

    def __init__(self, *args, request=None,  **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].required = False
        self.fields['category'].required = False
        try :
            subdomain_name= request.session.get('subdomain')
            self.fields['category'].initial = Category.objects.filter(name=subdomain_name)[0]
        except Exception as err :
            logger.error(f"{ str(err)}")

        instance = self.instance
        if not request == None :
            self.request = request
        self.fields['category'].disabled = True
        self.fields['title'].widget = forms.HiddenInput();

    def clean(self,*args,**kwargs):
        cleaned_data = super().clean()
        cleaned_data['title'] = cleaned_data.get('name')
        return cleaned_data

 
