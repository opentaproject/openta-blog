from django.contrib import admin
from blog.models import Category, Comment, Post, Visit

class CategoryAdmin(admin.ModelAdmin):
    pass

class PostAdmin(admin.ModelAdmin):
    list_display = ['title','last_modified','author','category']
    readonly_fields = ['created_on', 'last_modified']  # Replace with your field names
    pass

class CommentAdmin(admin.ModelAdmin):
    pass

class VisitAdmin(admin.ModelAdmin):
    list_display = ['visitor','post','date']
    pass

admin.site.register(Category, CategoryAdmin)
admin.site.register(Visit, VisitAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)
