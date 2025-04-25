from django.db import models
from django.db import transaction, IntegrityError
import time
import tiktoken
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import hashlib
import openai 
from openai import OpenAI
from django.db.models.signals import m2m_changed, pre_delete
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
    ntokens = models.IntegerField(default=0,null=True, blank=True)
    

    def __str__(self):
        return f"{self.original_file_name}"




    def save( self, *args, **kwargs ):
        is_new = self._state.adding  and not self.pk
        self.original_file_name = self.file.name
        self.path = self.file.path
        super().save(*args, **kwargs)  # Save first, so file is processed
        if is_new and self.file:
            data = self.file.read()
            self.checksum = hashlib.md5(data).hexdigest()
            uploaded_file = openai.files.create( file=open( self.file.path, "rb"), purpose="assistants")
            self.file_id = uploaded_file.id
            self.path = self.file.path
            encoding = tiktoken.encoding_for_model(settings.AI_MODEL)
            self.ntokens = len( encoding.encode(data.decode('utf-8' )) )

            print(f"PATH = { self.path}")
            super().save(*args, **kwargs) # Then update with true hashed path




@receiver(pre_delete, sender=OpenAIFile)
def custom_delete_openaifile(sender, instance, **kwargs):
    print(f"CUSTOM_DELETE_OPENAIFILE")
    pk = instance.pk
    file_id = instance.file_id 
    try :
        os.remove(instance.path)
    except Exception as e:
        logger.error(f" FILE/ {instance.path} DOES NOT EXIST")
    vst = VectorStore.objects.filter(files=instance)
    # THE VECTOR_STORE MUST BE 
    #ast = Assistant.objects.filter(vector_stores__in=vst)
    #for a in ast.all():
    #    pks = a.file_pks()
    #    assistant_id = a.assistant_id
    #    file_ids = []
    #    for pk_ in pks :
    #        if not pk_  == pk  :
    #            old_file_id = OpenTAFile.objects.get(pk=pk_).file_id
    #            print(f"OLD_FILE_ID = {old_file_id}")
    #            file_ids.append( old_file_id )
    #    print(f"FILE_IDS = {file_ids}")
    #    vs = client.vector_stores.create( name="{a.name}-merged", file_ids=file_ids)
    #    client.beta.assistants.update(
    #        assistant_id=assistant_id,
    #        tool_resources={"file_search": {"vector_store_ids": [ vs.id ] }},
    #        )
    for vs in vst.all() :
        vector_store_id = vs.vector_store_id
        try  :
            client.vector_stores.files.delete(vector_store_id=vector_store_id,file_id=file_id)
        except  openai.NotFoundError as e: 
            pass
    #
    #
    # When the  file is deleted, the vector stores are updated
    #

    try :
        client.files.delete(file_id)
        print(f"DELETED {instance.original_file_name}")
    except openai.NotFoundError as e:
        print(f"ERROR DELETING {instance.original_file_name}")
        pass

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
            ids.append(f.file_id)
        return ids

    def ntokens( self, *args, **kwargs ):
        files = self.files
        n = 0;
        for f in files.all():
            n = n + f.ntokens
        return n



    def file_pks(self, *args, **kwargs ):
        pks = []
        files = self.files
        for f in files.all():
            pks.append(f.pk)
        return pks

    def file_checksums(self, *args, **kwargs ):
        files = self.files
        pks = []
        for f in files.all():
            pks.append(f.checksum)
        return pks

    def files_ok( self, *args, **kwargs) :
        vs = self
        file_ids = vs.file_ids()
        print(f"FILE_IDS = {file_ids}")
        vector_store_id = vs.vector_store_id
        vector_store =  client.vector_stores.retrieve(vector_store_id)
        vector_store_files = client.vector_stores.files.list( vector_store_id=vector_store.id)
        remote_ids = []
        for f in vector_store_files:
            remote_ids.append( f.id)
        print(f"REMOTE_IDS = {remote_ids}")
        #assert  set( file_ids) == set( remote_ids) , f"{file_ids} == {remote_ids} is false "
        return set( file_ids) == set( remote_ids) 



    def save( self, *args, **kwargs ):
        is_new = self._state.adding and not self.pk
        print(f"IS_NEW = {is_new}")
        super().save(*args,**kwargs)
        print(f"DID SUPER SAVE")
        if is_new :
            vector_store = client.vector_stores.create(name=self.name)
            self.vector_store_id = vector_store.id
            super().save(*args,**kwargs)

@receiver(pre_delete, sender=VectorStore)
def custom_delete_vector_store(sender, instance, **kwargs):
    try :
        vector_store_id = instance.vector_store_id
        print(f"DELETE VECTOR_STORE{vector_store_id}")
        client.vector_stores.delete(vector_store_id=vector_store_id)
    except openai.NotFoundError as e:
        pass


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
            assistant = client.beta.assistants.create( name=self.name,
                instructions=self.instructions, 
                model=settings.AI_MODEL, 
                tools=[{"type": "file_search"}],)
            self.assistant_id = assistant.id
            super().save(*args,**kwargs)


    def ntokens( self, *args, **kwargs ):
        vs = self.vector_stores.all()
        n = 0;
        for v in vs :
            for vf in v.files.all():
                n = n + vf.ntokens 
        return n


    def file_pks( self, *args, **kwargs ):
        vs = self.vector_stores.all()
        f = []
        for v in vs :
            for vf in v.files.all():
                f.append( vf.pk )
        f = list( set( f) )
        return f

    def file_ids(self, *args, **kwargs ):
        vs = self.vector_stores.all()
        f = []
        for v in vs :
            for vf in v.files.all():
                f.append( vf.file_id )
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

    def remote_files( self, *args, **kwargs ) :
        assistant = self
        assistant_id = assistant.assistant_id
        remote_assistant = openai.beta.assistants.retrieve(assistant_id)
        tool_resources = remote_assistant.tool_resources
        remote_ids = [];
        vector_store_ids = tool_resources.file_search.vector_store_ids
        for vector_store_id in vector_store_ids :
            vector_store =  client.vector_stores.retrieve(vector_store_id)
            vector_store_files = client.vector_stores.files.list( vector_store_id=vector_store.id)
            for f in vector_store_files:
                remote_ids.append( f.id)
        return remote_ids


        

    def files_ok( self,*args, **kwargs):
        assistant = self
        file_ids = assistant.file_ids();
        remote_ids = assistant.remote_files();
        return set( remote_ids) == set( file_ids )


@receiver(pre_delete, sender=Assistant)
def custom_delete_assistant(sender, instance, **kwargs):
    pk = instance.pk
    assistant_id = instance.assistant_id
    assistant = openai.beta.assistants.retrieve(assistant_id)
    print(f"DELETE ASSISTANT {assistant}")
    tool_resources = assistant.tool_resources
    print(f"TOOL_RESOURCES = {tool_resources}")
    try :
        vector_store_id = tool_resources.file_search.vector_store_ids[0]
        print(f"VECTOR_STORES = {vector_store_id}")
        vector_store =  client.vector_stores.retrieve(vector_store_id)
        print(f"VECTOR_STORE = {vector_store}")
        print(f"VECTOR_STORE_NAME = {vector_store.name}")
        if vector_store.name == assistant_id : # THIS IS HERE BECAUSE MULTIPL VECTOR STORES CAN'T BE USED BY AN ASSISTANT
            client.vector_stores.delete(vector_store_id)
    except :
        pass
    client.beta.assistants.delete(assistant_id)


@receiver(m2m_changed, sender=Assistant.vector_stores.through)
def handle_assistants_changed(sender, instance, action, **kwargs):
    print(f"HANDLE_CHANGE_SENDER_ASSISTANT")
    if getattr(instance, '_updating_from_m2m', False):
        return
    instance._updating_from_m2m = True
    assistant_id = instance.assistant_id
    rebuild = False
    if action == "post_remove":
        vector_stores = instance.vector_stores.all();
        assistant_id = instance.assistant_id
        assistant = openai.beta.assistants.retrieve(assistant_id)
        tool_resources = assistant.tool_resources
        try :
            vector_store_id = tool_resources.file_search.vector_store_ids[0]
            vector_store =  client.vector_stores.retrieve(vector_store_id)
            client.vector_stores.delete(vector_store_id)
            print(f"REMAINING VECTOR_STORES TO BE SET UP {vector_stores}")
        except :
            print(f"ERROR DELTING")
            pass
        rebuild = True
        #
        # TODO RESTORE THE VECTOR STORE HERE
        #

    if action == "post_add" or rebuild:
        pks = [];
        ids = [];
        file_ids = [];
        file_pks = []
        for f in instance.vector_stores.all() :
            file_ids.extend( f.file_ids() )
            file_pks.extend( f.file_pks() )
            pks.append( f.pk )
            ids.append( f.vector_store_id );
        file_ids = list( set( file_ids ) )
        file_ids.sort() 
        file_pks = list( set( file_pks ) )
        print(f"IDS = {ids}")
        if len( ids ) < 2 :
            assistant = client.beta.assistants.update(
                assistant_id=assistant_id,
                tool_resources={"file_search": {"vector_store_ids": ids }},
                )
        else :
            vs = client.vector_stores.create( name=f"{assistant_id}", file_ids=file_ids)
            assistant = client.beta.assistants.update(
                assistant_id=assistant_id,
                tool_resources={"file_search": {"vector_store_ids": [ vs.id ] }},
                )

    instance.save()
    del instance._updating_from_m2m





@receiver(m2m_changed, sender=VectorStore.files.through)
def handle_files_changed(sender, instance, action, **kwargs):
    print(f"HANDLE_SENDER_VECTOR_STORE action={action} ")
    if True or action == "post_add":
        if getattr(instance, '_updating_from_m2m', False):
            return
        instance._updating_from_m2m = True
        vector_store_id = instance.vector_store_id
        vector_store_files = client.vector_stores.files.list( vector_store_id=vector_store_id)
        old_file_ids = []
        for vector_store_file in vector_store_files :
            file_id = vector_store_file.id
            old_file_ids.append(file_id)
            #try :
            #    client.vector_stores.files.delete( vector_store_id=vector_store_id, file_id=file_id)
            #except :
            #    print(f"FILE ERROR {file_id}")
        new_file_ids = []
        for f in instance.files.all() :
            new_file_ids.append( f.file_id )
        print(f"OLD_FILE_IDS = {old_file_ids} ")
        print(f"NEW_FILE_IDS = {new_file_ids} ")
        pks = [];
        ids = [];
        cksums = []
        for f in instance.files.all() :
            pks.append( f.pk )
            ids.append( f.file_id );
            cksums.append( f.checksum)
        added_files = list( set( new_file_ids) - set( old_file_ids ) )
        subtracted_files = list( set( old_file_ids)  - set( new_file_ids) )
        print(f"ADDED_FILES = {set(added_files)}")
        print(f"SUBTRACTED_FILES = {set(subtracted_files)}")
        for file_id in subtracted_files :
            client.vector_stores.files.delete( vector_store_id=vector_store_id, file_id=file_id)
        for file_id in added_files :
            client.vector_stores.files.create( vector_store_id=vector_store_id, file_id=file_id)



        ids = list( set(ids ))
        pks = list( set(pks) )
        cksums = list( set( cksums) )
        cksums.sort()
        ckstring = ''.join(cksums).encode()
        checksum = hashlib.md5(ckstring).hexdigest()
        instance.checksum = checksum
        #others = VectorStore.objects.filter(checksum=checksum)
        npks =  list( OpenAIFile.objects.filter(file_id__in=ids).values_list('pk',flat=True)  )
        print(f"IDS = {ids} PKS = {pks}")
        #
        # DO NOT MAKE CHECKSUM EQUIVALINCE OF DIFFERENT VECTOR STORES
        # SINCE THEY MAY CHANGE INDIVIDUALLY LATER
        #
        #if others.count() > 0 :
        #    other = others.last() 
        #    instance.vector_store_id = other.vector_store_id
        #    instance.files.add( *npks )
        #    instance.save()
        #    return
        #print(f"IDS TO BE ADDED TO VS = {ids}")
        #for fid in ids:
        #    try :
        #        client.vector_stores.files.create( vector_store_id=vector_store_id, file_id=fid)
        #    except :
        #        pass
        #instance.files.add( *pks )
        #instance.save()
        del instance._updating_from_m2m
        try :
            files = client.vector_stores.files.list(vector_store_id=vector_store_id)
        except :
            files = []

        is_done = False;
        i = 0;
        while not is_done  and i < 20 :
            is_done = True
            i = i + 1;
            for f in files:
                if f.status == 'in_progress' :
                    is_done = False 
            time.sleep(1)

