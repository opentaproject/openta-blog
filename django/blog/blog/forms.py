# blog/forms.py

from django import forms
from django_ckeditor_5.widgets import CKEditor5Widget
from .models import Comment, Post

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

      def __init__(self, *args, is_staff=None, **kwargs):
          print(f"ARGS = {args}")
          print(f"KWARGS = {kwargs}")
          super().__init__(*args, **kwargs)
          self.fields["body"].required = True
          self.fields["title"].required = True
          self.fields["post_author"].required = True
          self.fields['post_author'].selected = 1
          #self.fields["post_author"].widgetv = forms.HiddenInput();
          postauthor = self.fields["post_author"];
          print(f"POST_AUTHOR = {postauthor}")
          self.fields["is_staff"].required = False
          #self.fields['is_staff'].widget = forms.HiddenInput();
          if False and  not is_staff :
            self.fields['author_type'].widget = forms.HiddenInput();
            self.fields['category'].widget = forms.HiddenInput();
            self.is_staff = is_staff
                

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
          #fields = ['author_type','visibility','post_author','title','body','category' ]
          fields = '__all__'
          widgets = {
              "body": CKEditor5Widget( attrs={"class": "django_ckeditor_5"}, config_name="extends"),
              #"category": forms.HiddenInput(),
              #"author_type": forms.HiddenInput()

          }
