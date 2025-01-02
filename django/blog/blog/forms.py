# blog/forms.py

from django import forms
from django_ckeditor_5.widgets import CKEditor5Widget
from .models import Comment, Post

class CommentForm(forms.ModelForm):
      """Form for comments to the article."""

      def __init__(self, *args, **kwargs):
          super().__init__(*args, **kwargs)
          self.fields["body"].required = False
          self.fields["author"].required = False

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

      def __init__(self, *args, **kwargs):
          super().__init__(*args, **kwargs)
          self.fields["body"].required = True
          self.fields["title"].required = True

      def clean(self):
          cleaned_data = super().clean()
          body = cleaned_data.get('body')
          title = cleaned_data.get('title')
  
          if body and title:
              return cleaned_data
          else :
              raise forms.ValidationError("Title and body must be set.")
          

      class Meta:
          model = Post
          fields = '__all__' 
          widgets = {
              "body": CKEditor5Widget(
                  attrs={"class": "django_ckeditor_5"}, config_name="extends"
              )
          }
