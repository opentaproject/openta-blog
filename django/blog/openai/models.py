from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.storage import FileSystemStorage
import hashlib
import os



upload_storage = FileSystemStorage('/subdomain-data/sidecar/openaifiles', base_url="/")

def hashed_upload_to(instance, filename):
    file = instance.file
    file.open('rb')
    file_hash = hashlib.md5(file.read()).hexdigest()[0:6]
    file.seek(0)  # reset for saving later
    ext = os.path.splitext(filename)[1]
    return f'{file_hash}{ext}'

class OpenAIFile (models.Model) :
    date = models.DateTimeField(auto_now=True)
    checksum = models.CharField(primary_key=True, max_length=255,blank=True)
    original_file_name = models.CharField(max_length=255,blank=True)
    path = models.CharField(max_length=255,blank=True)
    file_key = models.CharField(max_length=255,blank=True)
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
            self.file_key = 'file_key'
            super().save(*args, **kwargs)
