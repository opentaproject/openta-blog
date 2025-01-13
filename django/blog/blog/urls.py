# blog/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path("", views.blog_index, name="blog_index"),
    path("blog/<category_selected>/", views.blog_index, name="blog_index"),
    path("blog/<category_selected>/<filter_key>", views.blog_index, name="blog_index"),
    path("add_post/", views.blog_add_post, name="blog_add_post"),
    path("edit_post/<int:pk>/", views.blog_edit_post, name="blog_edit_post"),
    path("delete_post/<int:pk>/", views.blog_delete_post, name="blog_delete_post"),
    path("blog_leave_comment/<int:pk>/", views.blog_leave_comment, name="blog_leave_comment"),
    path("blog_delete_comment/<int:pk>/", views.blog_delete_comment, name="blog_delete_comment"),
    path("post/<int:pk>/", views.blog_index, name="blog_index"),
    path("comment/<int:pk>/", views.blog_edit_comment, name="blog_edit_comment"),
    path("category/<category>/", views.blog_category, name="blog_category"),
]
