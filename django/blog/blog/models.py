from django.db import models
from django_ckeditor_5.fields import CKEditor5Field
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=30)
    class Meta:
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name
    

class Post(models.Model):
    title = models.CharField(max_length=255)
    body = CKEditor5Field('Text', config_name='extends')
    created_on = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    categories = models.ForeignKey("Category", on_delete=models.CASCADE,null=True, blank=True,  related_name="posts")

    def __str__(self):
        return self.title

class Comment(models.Model):
    author = models.CharField(max_length=60)
    #user =  models.ForeignKey(User , null=True, blank=True, on_delete=models.CASCADE)
    body =   CKEditor5Field('Text', config_name='extends')
    created_on = models.DateTimeField(auto_now_add=True)
    post = models.ForeignKey("Post", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.author} on '{self.post}'"
