from django.contrib import admin
from django.urls import path,include
from django.urls import re_path as url
from backend import views 
from filebrowser.sites import site
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('admin/filebrowser/', site.urls),
    path('admin/', admin.site.urls),
    path('grappelli/', include('grappelli.urls')),
    path('config_lti',views.config_lti,name='config_lti'),
    path('', include('users.urls')),
    path("", include("blog.urls")),
    path('lti_landing/', views.lti_landing, name='lti_landing'),
    path('lti/', include('lti_provider.urls'))
    
]


urlpatterns += [
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += [
    path("ckeditor5/", include('django_ckeditor_5.urls')),
]

