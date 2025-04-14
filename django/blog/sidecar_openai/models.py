from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import hashlib
import openai 
from openai import OpenAI

import os
client = openai.OpenAI(api_key=settings.AI_KEY)



upload_storage = FileSystemStorage('/subdomain-data/sidecar/openaifiles', base_url="/")

def hashed_upload_to(instance, filename):
    file = instance.file
    file.open('rb')
    file_hash = hashlib.md5(file.read()).hexdigest()[0:8]
    file.seek(0)  # reset for saving later
    ext = os.path.splitext(filename)[1]
    return f'{file_hash}{ext}'

class OpenAIFile(models.Model) :
    date = models.DateTimeField(auto_now=True)
    checksum = models.CharField(primary_key=True, max_length=255,blank=True)
    original_file_name = models.CharField(max_length=255,blank=True)
    path = models.CharField(max_length=255,blank=True)
    file_id = models.CharField(max_length=255,blank=True)
    file = models.FileField( max_length=512, upload_to=hashed_upload_to, storage=upload_storage,)



    def save( self, *args, **kwargs ):
        is_new = self._state.adding and not self.pk
        self.original_file_name = f"{self.file}"
        super().save(*args, **kwargs)  # Save first, so file is processed
        
        if is_new and self.file:
            data = self.file.read()
            print(f"FILE = {self.file}")
            self.checksum = hashlib.md5(data).hexdigest()
            self.path = self.file.path
            #uploaded_file = openai.files.create( file=open( self.path, "rb"), purpose="assistants")
            self.file_id = 'file_id'
            super().save(*args, **kwargs) # Then update with true hashed path

#class VectorStore( models.model ):
#    vector_store_id = models.CharField(max_length=255,blank=True)
#    files = ManyToManyFields( OpenTAFile )
# 
#
#
#    vector_store = client.vector_stores.create(name="Simple file")
#    vector_store_id = vector_store.id

