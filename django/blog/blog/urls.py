# blog/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path("", views.blog_index, name="blog_index"),
    path("blog/<category_selected>/", views.blog_index, name="blog_index"),
    path("add_post/", views.blog_add_post, name="blog_add_post"),
    path("edit_post/<int:pk>/", views.blog_edit_post, name="blog_edit_post"),
    path("post/<int:pk>/", views.blog_view_post, name="blog_view_post"),
    path("comment/<int:pk>/", views.blog_edit_comment, name="blog_edit_comment"),
    path("category/<category>/", views.blog_category, name="blog_category"),
]
