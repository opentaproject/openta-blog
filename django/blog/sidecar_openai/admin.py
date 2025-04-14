from django.contrib import admin
from .models import OpenAIFile  # Replace with your actual model

@admin.register(OpenAIFile)
class OpenAIFileAdmin(admin.ModelAdmin):
    readonly_fields = ('checksum','original_file_name','path')
