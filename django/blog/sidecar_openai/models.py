from django.db import models
import time
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import hashlib
import openai 
from openai import OpenAI
from django.db.models.signals import m2m_changed
from django.dispatch import receiver

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
    checksum = models.CharField(blank=True, max_length=255)
    original_file_name = models.CharField(max_length=255,blank=True)
    path = models.CharField(max_length=255,blank=True)
    file_id = models.CharField(max_length=255,blank=True)
    file = models.FileField( max_length=512, upload_to=hashed_upload_to, storage=upload_storage,)



    def save( self, *args, **kwargs ):
        is_new = self._state.adding  and not self.pk
        self.original_file_name = self.file.name
        super().save(*args, **kwargs)  # Save first, so file is processed
        if is_new and self.file:
            data = self.file.read()
            print(f"FILE = {self.file}")
            self.checksum = hashlib.md5(data).hexdigest()
            others = OpenAIFile.objects.filter(checksum=self.checksum )
            if others.count() > 0 :
                print(f"GOT IDENTICAL FILE")
                other = others.last() 
                self.file_id = other.file_id
                self.path = other.path
                if os.path.exists( self.file.path ):
                    os.remove( self.file.path )
            else :
                uploaded_file = openai.files.create( file=open( self.path, "rb"), purpose="assistants")
                self.file_id = uploaded_file.id
                self.path = self.file.path
            super().save(*args, **kwargs) # Then update with true hashed path

class VectorStore( models.Model ):
    vector_store_id = models.CharField(max_length=255,blank=True)
    name =  models.CharField(max_length=255,blank=True)
    files = models.ManyToManyField( OpenAIFile )

    def save( self, *args, **kwargs ):
        is_new = self._state.adding and not self.pk
        super().save(*args,**kwargs)
        if is_new :
            print(f"{self.files.all() }")
            vector_store = client.vector_stores.create(name=self.name)
            self.vector_store_id = vector_store.id
            super().save(*args,**kwargs)

@receiver(m2m_changed, sender=VectorStore.files.through)
def handle_files_changed(sender, instance, action, **kwargs):
    if action == "post_add":
        if getattr(instance, '_updating_from_m2m', False):
            return
        instance._updating_from_m2m = True
        print(f"Files updated for VectorStore: {instance.pk}")
        print(f"FILES = {instance.files.all() }")
        vector_store_id = instance.vector_store_id
        print(f"VECTOR_STORE_ID = {vector_store_id}")
        pks = [];
        ids = [];
        for f in instance.files.all() :
            pks.append( f.pk )
            ids.append( f.file_id );
            print(f"F = {f.pk} {f.file_id} ")
        print(f"PKS = {pks}")
        print(f"IDS = {ids }")
        for fid in ids:
            client.vector_stores.files.create( vector_store_id=vector_store_id, file_id=fid)
        instance.files.add( *pks )
        instance.save()
        del instance._updating_from_m2m
        print("CHECK!")
        files = client.vector_stores.files.list(vector_store_id=vector_store_id)
        is_done = False;
        i = 0;
        while not is_done  and i < 20 :
            is_done = True
            i = i + 1;
            for f in files:
                if f.status == 'in_progress' :
                    is_done = False 
                print("CHECK THE UPLOAD ", f.id, f.status)
            time.sleep(1)

