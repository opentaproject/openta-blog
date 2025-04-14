from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.storage import FileSystemStorage


upload_storage = FileSystemStorage('/subdomain-data/sidecar/openaifiles', base_url="/")

class OpenAIFile (models.Model) :
    date = models.DateTimeField(auto_now=True)
    checksum = models.CharField(primary_key=True, max_length=255,blank=True)
    file_name = models.CharField(max_length=255,blank=True)
    path = models.CharField(max_length=255,blank=True)
    file_key = models.CharField(max_length=255,blank=True)
    file = models.FileField( max_length=512, storage=upload_storage,)



    def save( self, *args, **kwargs ):
        self.checksum = 'checksum'
        self.file_name = 'file_name'
        self.path = 'path'
        self.file_key = 'file_key'
        super().save(*args, **kwargs)
