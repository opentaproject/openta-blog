from django.contrib import admin
from .models import OpenAIFile  # Replace with your actual model

@admin.register(OpenAIFile)
class OpenAIFileAdmin(admin.ModelAdmin):
    readonly_fields = ('checksum','file_name','path','file_key') 
