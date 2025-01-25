# blog/forms.py

from django import forms
from django_ckeditor_5.widgets import CKEditor5Widget
from .models import Comment, Post
import logging
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

      def __init__(self,   *args, is_staff=None, alias='',  **kwargs ):
          print(f"ALIAS IN __INIT__  = {alias}")
          kwargs.setdefault('label_suffix', 'ABC') 
          kwargs['label_suffix'] = ''
          logger.error(f"POST_FORM ARGS = {args}")
          logger.error(f"POST_FORM KWARGS = {kwargs}")
          super().__init__(*args, **kwargs)
          print(f"INIT")
          for k in self.fields.keys() :
              print(f" K = {k} val = {self.fields[k]}")
          self.fields["body"].required = True
          self.fields["title"].required = True
          self.fields["alias"].required = False
          self.fields["alias"].initial = alias
          self.fields["post_author"].required = True
          self.fields["is_staff"].required = False
          self.fields["filter_key"].required = False
          self.fields["filter_key"].widget = forms.MultipleHiddenInput();
          for k in [ 'author_type', 'post_author','body','category','filter_key','is_staff'] :
              self.fields[k].label = ''
          self.fields["title"].label = 'Title: '
          self.fields["visibility"].label = 'Visibility: '
          self.fields["alias"].label = 'Alias: '
          self.fields["visibility"].label_class= 'text-xs'
          self.fields["title"].label_class= 'text-xs'
          self.fields["visibility"].widget = forms.RadioSelect(choices=self.OPTIONS,attrs=({'class' : 'px-2 gap-4 inline-flex'})  )
          if True or not is_staff :
            self.fields['author_type'].widget = forms.HiddenInput({'label' : '' } );
            self.fields['category'].widget = forms.HiddenInput();
            self.is_staff = is_staff
            self.fields["is_staff"].widget = forms.HiddenInput();
            self.fields["post_author"].widget = forms.HiddenInput();
                

      def clean(self):
          cleaned_data = super().clean()
          print(f"CLEAN {cleaned_data}")
          body = cleaned_data.get('body')
          title = cleaned_data.get('title')
          alias = cleaned_data.get('alias')
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
