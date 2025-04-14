from django.contrib import admin
from .models import OpenAIFile  , VectorStore # Replace with your actual model

@admin.register(OpenAIFile)
class OpenAIFileAdmin(admin.ModelAdmin):
    list_display = ('pk', 'original_file_name', 'file_id', 'date')
    readonly_fields = ('checksum','original_file_name','path','file_id')

@admin.register(VectorStore)
class VectorStoreAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'vector_store_id', 'list_file_ids')  # Add your custom method here

    def list_file_ids(self, obj):
        return ", ".join(str(f.pk) for f in obj.files.all())

    list_file_ids.short_description = "File IDs"
    
