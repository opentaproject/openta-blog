from django.db import models
from django.db import transaction, IntegrityError
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

    def __str__(self):
        return f"{self.original_file_name}"




    def save( self, *args, **kwargs ):
        is_new = self._state.adding  and not self.pk
        self.original_file_name = self.file.name
        super().save(*args, **kwargs)  # Save first, so file is processed
        if is_new and self.file:
            data = self.file.read()
            #print(f"FILE = {self.file}")
            self.checksum = hashlib.md5(data).hexdigest()
            others = OpenAIFile.objects.filter(checksum=self.checksum )
            if others.count() > 0 :
                #print(f"GOT IDENTICAL FILE")
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
    checksum = models.CharField(blank=True, max_length=255)
    vector_store_id = models.CharField(max_length=255,blank=True)
    name =  models.CharField(max_length=255,unique=True)
    files = models.ManyToManyField( OpenAIFile )

    def __str__(self):
        return f"{self.name}"

    def file_ids(self, *args, **kwargs ):
        files = self.files
        ids = []
        for f in files.all():
            #print(f"I {f.file_id}")
            ids.append(f.file_id)
        return ids

    def file_pks(self, *args, **kwargs ):
        files = self.files
        pks = []
        for f in files.all():
            #print(f"I {f.file_id}")
            pks.append(f.pk)
        return pks

    def file_checksums(self, *args, **kwargs ):
        files = self.files
        pks = []
        for f in files.all():
            #print(f"I {f.file_id}")
            pks.append(f.checksum)
        return pks





    def save( self, *args, **kwargs ):
        is_new = self._state.adding and not self.pk
        super().save(*args,**kwargs)
        if is_new :
            #print(f"{self.files.all() }")
            vector_store = client.vector_stores.create(name=self.name)
            self.vector_store_id = vector_store.id
            super().save(*args,**kwargs)

class Assistant( models.Model ):
    name =   models.CharField(max_length=255,blank=True)
    instructions = models.TextField(blank=True)
    vector_stores = models.ManyToManyField( VectorStore )
    assistant_id = models.CharField(max_length=255,blank=True)
    json_field = models.JSONField( default=dict ,  blank=True, null=True)

    def save( self, *args, **kwargs ):
        is_new = self._state.adding and not self.pk
        self.json_field = "{}"
        super().save(*args,**kwargs)
        if is_new :
            #print(f"{self.vector_stores.all() }")
            assistant = client.beta.assistants.create( name=self.name,
                instructions=self.instructions, 
                model=settings.AI_MODEL, 
                tools=[{"type": "file_search"}],)
            self.assistant_id = assistant.id
            super().save(*args,**kwargs)


    def file_pks( self, *args, **kwargs ):
        vs = self.vector_stores.all()
        f = []
        for v in vs :
            for vf in v.files.all():
                f.append( vf.pk )
        f = list( set( f) )
        return f


    def file_names( self, *args, **kwargs ):
        vs = self.vector_stores.all()
        f = []
        for v in vs :
            for vf in v.files.all():
                f.append( vf.original_file_name )
        f = list( set( f) )
        return f

@receiver(m2m_changed, sender=Assistant.vector_stores.through)
def handle_vector_stores_changed(sender, instance, action, **kwargs):
    if action == "post_add":
        if getattr(instance, '_updating_from_m2m', False):
            return
        instance._updating_from_m2m = True
        #print(f"VectorStore updated for Admin: {instance.pk}")
        #print(f"VectorStores = {instance.vector_stores.all() }")
        assistant_id = instance.assistant_id
        #print(f"ASSISTANT_ID = {assistant_id}")
        pks = [];
        ids = [];
        file_ids = [];
        file_pks = []
        for f in instance.vector_stores.all() :
            file_ids.extend( f.file_ids() )
            file_pks.extend( f.file_pks() )
            #print(f"FILE_IDS = {f.file_ids()}")
            pks.append( f.pk )
            ids.append( f.vector_store_id );
            #print(f"F = {f.pk} {f.vector_store_id} ")
        #print(f"PKS = {pks}")
        #print(f"IDS = {ids }")
        #print(f"FILE_IDS = {file_ids}")
        file_ids = list( set( file_ids ) )
        file_ids.sort() 
        file_pks = list( set( file_pks ) )
        #print(f"FILE_IDS IS NOW {file_ids}")
        #print(f"FILE_PKS IS NOW {file_pks}")
        if len( ids ) < 2 :
            assistant = client.beta.assistants.update(
                assistant_id=assistant_id,
                tool_resources={"file_search": {"vector_store_ids": ids }},
                )
        else :
            #print(f"UPDATE WITH FILE_IDS = {file_ids}")
            #vsname= f"merged-{instance.name}"
            #try:
            #    with transaction.atomic():
            #        Vs, _ = VectorStore.objects.get_or_create(name=vsname)
            #except Exception as err :
            #        Vs = VectorStore.objects.get(name=vsname)
            #vfiles = OpenAIFile.objects.filter(pk__in=file_pks)
            #print(f"VFILES = {file_pks}")
            #Vs.files.set(file_pks)
            #Vs.save()
            vs = client.vector_stores.create( name="merged_vs {instance.name}", file_ids=file_ids)
            assistant = client.beta.assistants.update(
                assistant_id=assistant_id,
                tool_resources={"file_search": {"vector_store_ids": [ vs.id ] }},
                )

        instance.save()
        del instance._updating_from_m2m
        is_done = False;
        i = 0;
        #print(assistant.tool_resources.file_search.vector_store_ids)
        #while not is_done  and i < 20 :
        #    is_done = True
        #    i = i + 1;
        #    for f in files:
        #        if f.status == 'in_progress' :
        #            is_done = False 
        #        print("CHECK THE UPLOAD ", f.id, f.status)
        #    time.sleep(1)





@receiver(m2m_changed, sender=VectorStore.files.through)
def handle_files_changed(sender, instance, action, **kwargs):
    if action == "post_add":
        if getattr(instance, '_updating_from_m2m', False):
            return
        instance._updating_from_m2m = True
        #print(f"Files updated for VectorStore: {instance.pk}")
        #print(f"FILES = {instance.files.all() }")
        vector_store_id = instance.vector_store_id
        #print(f"VECTOR_STORE_ID = {vector_store_id}")
        pks = [];
        ids = [];
        cksums = []
        for f in instance.files.all() :
            pks.append( f.pk )
            ids.append( f.file_id );
            cksums.append( f.checksum)
            #print(f"F = {f.pk} {f.file_id} ")
        #print(f"PKS = {pks}")
        #print(f"IDS = {ids }")
        #print(f"CHCKSUMS = {cksums}")
        ids = list( set(ids) )
        pks = list( set(pks) )
        cksums = list( set( cksums) )
        cksums.sort()
        ckstring = ''.join(cksums).encode()
        #print(f"CKSTRING = {ckstring}")
        checksum = hashlib.md5(ckstring).hexdigest()
        instance.checksum = checksum
        #print(f"CKSUMS IS NOW {cksums}")
        #print(f"ids iIS NOW {ids}")
        others = VectorStore.objects.filter(checksum=checksum)
        npks =  list( OpenAIFile.objects.filter(file_id__in=ids).values_list('pk',flat=True)  )
        if others.count() > 0 :
            #print(f"GOT IDENTICAL Checksum pks = {npks} ")
            other = others.last() 
            instance.vector_store_id = other.vector_store_id
            instance.files.add( *npks )
            instance.save()
            return
        for fid in ids:
            client.vector_stores.files.create( vector_store_id=vector_store_id, file_id=fid)
        instance.files.add( *pks )
        instance.save()
        del instance._updating_from_m2m
        #print("CHECK!")
        files = client.vector_stores.files.list(vector_store_id=vector_store_id)
        is_done = False;
        i = 0;
        while not is_done  and i < 20 :
            is_done = True
            i = i + 1;
            for f in files:
                if f.status == 'in_progress' :
                    is_done = False 
                #print("CHECK THE UPLOAD ", f.id, f.status)
            time.sleep(1)

