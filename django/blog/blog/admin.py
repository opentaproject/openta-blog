from django.contrib import admin
from blog.models import Category, Comment, Post, Visit

class CategoryAdmin(admin.ModelAdmin):
    pass

class PostAdmin(admin.ModelAdmin):
    pass

class CommentAdmin(admin.ModelAdmin):
    pass

class VisitAdmin(admin.ModelAdmin):
    pass

admin.site.register(Category, CategoryAdmin)
admin.site.register(Visit, VisitAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)
