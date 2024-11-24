# blog/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path("", views.blog_index, name="blog_index"),
    path("blog/<category_selected>/", views.blog_index, name="blog_index"),
    path("post/<int:pk>/", views.blog_leave_comment, name="blog_leave_comment"),
    path("comment/<int:pk>/", views.blog_edit_comment, name="blog_edit_comment"),
    path("category/<category>/", views.blog_category, name="blog_category"),
]
