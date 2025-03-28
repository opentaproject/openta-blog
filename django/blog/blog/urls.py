# blog/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path("", views.blog_index, name="blog_index"),
    path("toggle_resolved/<val>/<pk>/", views.toggle_resolved, name="toggle_resolved"),
    path("blog/<category_selected>/", views.blog_index, name="blog_index"),
    path("blog/home/", views.blog_index, name="blog_index"),
    path("sidecar_count/", views.sidecar_count , name="sidecar_count"),
    path("home/", views.blog_index, name="blog_index"),
    path("blog/<category_selected>/<filter_key>", views.blog_index, name="blog_index"),
    path("add_post/", views.blog_add_post, name="blog_add_post"),
    path("edit_post/<int:pk>/", views.blog_edit_post, name="blog_edit_post"),
    path("delete_post/<int:pk>/", views.blog_delete_post, name="blog_delete_post"),
    path("blog_leave_comment/<int:pk>/", views.blog_leave_comment, name="blog_leave_comment"),
    path("blog_delete_comment/<int:pk>/", views.blog_delete_comment, name="blog_delete_comment"),
    path("post/<int:pk>/", views.blog_index, name="blog_index"),

    path("filter_key/comment/<int:pk>/", views.blog_edit_comment, name="blog_edit_comment"),
    path('filter_key/create/', views.FilterKeyCreateView.as_view(), name='filter_key_create'),
    path('filter_key/<int:pk>/update/', views.FilterKeyUpdateView.as_view(), name='filter_key_update'),
    path('filter_key/<int:pk>/delete/', views.FilterKeyDeleteView.as_view(), name='filter_key_delete'),
    path('filter_key/list/', views.FilterKeyListView.as_view(), name='filter_key_list'),
    path('filter_key/list/<subdomain>/', views.FilterKeyListView.as_view(), name='filter_key_list'),

    path('category/create/', views.CategoryCreateView.as_view(), name='category_create'),
    path('category/<int:pk>/update/', views.CategoryUpdateView.as_view(), name='category_update'),
    path('category/<int:pk>/delete/', views.CategoryDeleteView.as_view(), name='category_delete'),
    path('category/list/', views.CategoryListView.as_view(), name='category_list'),
    path('category/list/<subdomain>/', views.CategoryListView.as_view(), name='category_list'),

    ]


