# blog/forms.py

from django import forms
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
          fk = [ i['pk'] for i in list( instance.filter_key.all().values('pk') ) ]
          kwargs.setdefault('label_suffix', 'ABC') 
          kwargs['label_suffix'] = ''
          logger.error(f"POST_FORM ARGS = {args}")
          logger.error(f"POST_FORM KWARGS = {kwargs}")
          super().__init__(*args, **kwargs)
          #for k in self.fields.keys() :
          #    print(f" K = {k} val = {self.fields[k]}")
          self.fields["body"].required = True
          self.fields["title"].required = True
          self.fields["alias"].required = False
          self.fields["alias"].initial = alias
          self.fields["post_author"].required = True
          self.fields["is_staff"].required = False
          self.fields["filter_key"].required = False
          #self.fields["filter_key"].widget = forms.SelectMultiple();
          for k in [ 'author_type', 'post_author','body','category','is_staff'] :
              self.fields[k].label = ''
          self.fields["filter_key"].initial = kwargs['initial']['filter_key']
          self.fields["title"].label = 'Title: '
          self.fields["visibility"].label = 'Visibility: '
          self.fields["alias"].label = 'Alias: '
          self.fields["title"].widget=forms.TextInput(attrs={'class': 'OpenTA-text-input' });
          self.fields["alias"].widget=forms.TextInput(attrs={'class': 'OpenTA-text-input',});
          self.fields["visibility"].widget = forms.RadioSelect(choices=self.OPTIONS);
          #self.fields["title"].widget.attrs.update({'class' : 'OpenTA-title',})
          #self.fields["alias"].widget.attrs.update({'class' : 'OpenTA-alias'})
          #print(f'FILTER_KEY_IN_FORM = { self.fields["filter_key"].choices }')
          #self.fields["filter_key"].queryset = FilterKey.objects.filter(category=instance.category) # FIX THIS
          category = instance.category
          print(f"CATEGORY = {category}")
          subdomain = category.subdomain
          categories = Category.objects.filter(subdomain=subdomain)
          filter_keys = FilterKey.objects.all();
          #filter_keys =  filter_keys.filter(category__in=categories) 
          f = list( filter_keys.values_list('name',flat=True) )
          f = [i for i in f if re.match(r"^\w{8}-\w{4}-\w{4}-\w{4}-\w{12}",i) ] # THIS EXCLUDES THE AUTOMATICALLY GENERATED KEYS OF EXERCISES
          if settings.HIDE_UUID :
            filter_keys = filter_keys.exclude(name__in=f)
          self.fields["filter_key"].queryset = filter_keys
          print(f"CATEGORIES = {categories}")
          print(f"SUBDOMAIN = {subdomain}")
          if True or not is_staff :
            self.fields['author_type'].widget = forms.HiddenInput({'label' : '' } );
            self.fields['category'].widget = forms.HiddenInput();
            self.is_staff = is_staff
            self.fields["is_staff"].widget = forms.HiddenInput();
            self.fields["post_author"].widget = forms.HiddenInput();
            #self.fields["filter_key"].widget.attrs.update({'class' : 'px-2 pb-2 text-red-400  ABCDEFG'} ,)
            #self.fields["filter_key"].widget.attrs.update(attrs)
                

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
          fields = ['author_type','visibility','post_author','title','body','category' ,'filter_key','alias']
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
            #self.fields['subdomain'].disabled = True
            subdomain_name = request.session.get('subdomain','')
            subdomain, _ = Subdomain.objects.get_or_create(name=subdomain_name)
            #self.fields['subdomain'] = subdomain
            instance.subdomain = subdomain
            self.fields['subdomain'].initial = subdomain
            #self.fields['subdomain'].widget = forms.HiddenInput();
        else :
            self.fields['subdomain'].initial = instance.subdomain
        #self.fields['subdomain'].widget = forms.HiddenInput();
        self.fields['restricted'].initial  = True
        self.fields['restricted'].required = False 
        self.fields['restricted'].disabled = True
        self.fields['subdomain'].disabled = True
        #if self.instance and self.instance.parent:
        #    self.fields['subdomain'].queryset = Subdomain.objects.filter(name=self.instance.parent)
        #else:
        #    self.fields['subdomain'].queryset = Subdomain.objects.none()

class FilterKeyForm(forms.ModelForm):

    class Meta:
        model = FilterKey
        fields = '__all__'

    def __init__(self, *args, request=None,  **kwargs):
        super().__init__(*args, **kwargs)
        instance = self.instance
        if not request == None :
            self.request = request
            subdomain_name = request.session.get('subdomain','')
            subdomain, _ = Subdomain.objects.get_or_create(name=subdomain_name)
        print(f"FILTER_KEY SUBDOMAIN = {subdomain}")
