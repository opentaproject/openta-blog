from django.contrib import admin
from blog.models import Category, Comment, Post, Visit, Visitor, Subdomain, FilterKey


class FilterKeyAdmin(admin.ModelAdmin):
    list_display = ['id','subdomain','category','title','name','get_posts']
    pass

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id','name','hidden','get_filterkeys']
    pass

class PostAdmin(admin.ModelAdmin):
    list_display = ['title','visibility','last_modified','post_author','category']
    readonly_fields = ['created_on', 'last_modified']  # Replace with your field names
    pass

class CommentAdmin(admin.ModelAdmin):
    list_display = ['id','comment_author','post','created_on']
    pass

class VisitAdmin(admin.ModelAdmin):
    list_display = ['id','visitor','post','date']
    pass

class SubdomainAdmin(admin.ModelAdmin):
    list_display = ['id','name']
    pass

class VisitorAdmin(admin.ModelAdmin):
    list_display = ['id','name','subdomain','last_visit','visitor_type']
    pass

admin.site.register(Category, CategoryAdmin)
admin.site.register(Visit, VisitAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Subdomain, SubdomainAdmin)
admin.site.register(FilterKey, FilterKeyAdmin)
admin.site.register(Visitor, VisitorAdmin)
