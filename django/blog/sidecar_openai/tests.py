from django.test import TestCase
import time
import os
from sidecar_openai.models import OpenAIFile, VectorStore, Assistant
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ObjectDoesNotExist

import openai
from openai import OpenAI


model = 'gpt-4o-mini'
client = OpenAI()
import string
import random


def randstring(length=8):
    characters = string.ascii_letters + string.digits  # A-Z, a-z, 0-9
    return ''.join(random.choices(characters, k=length))



class OpenAI(TestCase):
    def setUp( self ):
        User = get_user_model()
        self.admin_user = User.objects.create_superuser( username='admin', email='admin@example.com', password='adminpass')
        self.client.login(username='admin', password='adminpass')

    def notest_create_and_delete_file_object(self):
        url = reverse('admin:sidecar_openai_openaifile_changelist')  # use your app and model name
        response = self.client.get(url)
        #print(f"RESPONSE = {response}")
        url = reverse('admin:sidecar_openai_openaifile_add')  # use your app and model name
        test_file1 = SimpleUploadedFile( "test1.txt", b"test1_content_here\n", content_type="text/plain")
        self.client.post( url ,  {'file': test_file1}, follow=True)
        t1 = OpenAIFile.objects.get(original_file_name="test1.txt")
        file_id1 = t1.file_id
        try :
            aifile = client.files.retrieve(file_id1)
            exists = True
        except openai.OpenAIError as e:
            exists = False
        assert exists , f"{file_id1} Does not exist on server "
        path = t1.path
        #print(f"EXISTS = {exists} PATH={path} ")
        assert os.path.exists(path), f"LOCAL FILE PATH {path} DOES NOT EXIST"
        #print(f"NOW DELETE THE FILE")
        t1.delete();
        try :
            aifile = client.files.retrieve(file_id1)
            exists = True
        except openai.OpenAIError as e:
            exists = False
        #print(f"NOW EXISTS = {exists}")
        assert not exists, f"FILE {file_id1} was not successfully deleted on the server"
        try :
            t1 = OpenAIFile.objects.get(original_file_name="test1.txt")
            exists_locally = True
        except ObjectDoesNotExist as e :
            exists_locally = False
            #print(f"OK! text.txt IS GONE  LOCALLY ")
        assert not exists_locally, f"File {file_id1} still exists locally"
        assert not os.path.exists(path), f"LOCAL FILE PATH {path} DID NOT GET DELETED"




    def notest_create_and_delete_two_openai_file_objects(self):
        url = reverse('admin:sidecar_openai_openaifile_changelist')  # use your app and model name
        response = self.client.get(url)
        print(f"RESPONSE = {response}")
        url = reverse('admin:sidecar_openai_openaifile_add')  # use your app and model name
        test_file1 = SimpleUploadedFile( "test1.txt", b"test1_content_here\n", content_type="text/plain")
        self.client.post( url ,  {'file': test_file1}, follow=True)
        t1 = OpenAIFile.objects.get(original_file_name="test1.txt")
        test_file2 = SimpleUploadedFile( "test2.txt", b"test2_content_here\n", content_type="text/plain")
        self.client.post( url ,  {'file': test_file2}, follow=True)
        t2 = OpenAIFile.objects.get(original_file_name="test2.txt")
        for t in [t1,t2] :
            path = t.path
            original_file_name = t.original_file_name
            file_id = t.file_id
            t.delete();
            try :
                aifile = client.files.retrieve(file_id)
                exists = True
            except openai.OpenAIError as e:
                exists = False
            print(f"NOW EXISTS = {exists}")
            assert not exists, f"FILE {file_id} was not successfully deleted on the server"
            try :
                tt = OpenAIFile.objects.get(original_file_name=original_file_name)
                exists_locally = True
            except ObjectDoesNotExist as e :
                exists_locally = False
                print(f"OK! {original_file_name} is GONE  LOCALLY ")
            assert not exists_locally, f"File {file_id} still exists locally"
            assert not os.path.exists(path), f"LOCAL FILE PATH {path} DID NOT GET DELETED"






    def notest_create_and_delete_vector_store_object(self):
        url = reverse('admin:sidecar_openai_openaifile_changelist')  # use your app and model name
        response = self.client.get(url)
        print(f"RESPONSE = {response}")
        url = reverse('admin:sidecar_openai_openaifile_add')  # use your app and model name
        test_file1 = SimpleUploadedFile( "test1.txt", b"test1_content_here\n", content_type="text/plain")
        self.client.post( url ,  {'file': test_file1}, follow=True)
        t1 = OpenAIFile.objects.get(original_file_name="test1.txt")
        test_file2 = SimpleUploadedFile( "test2.txt", b"test2_content_here\n", content_type="text/plain")
        self.client.post( url ,  {'file': test_file2}, follow=True)
        t2 = OpenAIFile.objects.get(original_file_name="test2.txt")
        vsname = randstring()
        vs = VectorStore(name=vsname)
        vs.save()
        vs.files.set([t1,t2])
        vs.save()
        vs.files.add(t1) # REDUNDANT ADD
        vs.save()
        vs.files.add(t2); # REDUNDANT ADD
        vs.save()

        def ckfiles( vs ):
            file_ids = vs.file_ids()
            print(f"FILE_IDS = {file_ids}")
            vector_store_id = vs.vector_store_id
            vector_store =  client.vector_stores.retrieve(vector_store_id)
            vector_store_files = client.vector_stores.files.list( vector_store_id=vector_store.id)
            remote_ids = []
            for f in vector_store_files:
                remote_ids.append( f.id)
            print(f"REMOTE_IDS = {remote_ids}")
            return set( file_ids) == set( remote_ids) 

        assert vs.files_ok( ), "TWO FILES NOT OK"
        vs.files.remove( t1  )
        print(f"AFTER REMOVE t1 {vs.file_ids}")
        assert vs.files_ok() , "ONE FILE NOT OK"
        t2.delete()
        print(f"AFTERM REMOVING t2 {vs.file_ids}")
        assert vs.files_ok( ) , "NO FILES SHOULD BE LEFT"
        vs.delete()
        t1.delete()


    def notest_create_and_delete_assistant_object(self):
        url = reverse('admin:sidecar_openai_openaifile_changelist')  # use your app and model name
        response = self.client.get(url)
        print(f"RESPONSE = {response}")
        url = reverse('admin:sidecar_openai_openaifile_add')  # use your app and model name

        test_file1 = SimpleUploadedFile( "test1.txt", b"test1_content_here\n", content_type="text/plain")
        self.client.post( url ,  {'file': test_file1}, follow=True)
        t1 = OpenAIFile.objects.get(original_file_name="test1.txt")
        test_file2 = SimpleUploadedFile( "test2.txt", b"test2_content_here\n", content_type="text/plain")
        self.client.post( url ,  {'file': test_file2}, follow=True)
        t2 = OpenAIFile.objects.get(original_file_name="test2.txt")

        test_file3 = SimpleUploadedFile( "test3.txt", b"test3_content_here\n", content_type="text/plain")
        self.client.post( url ,  {'file': test_file3}, follow=True)
        t3 = OpenAIFile.objects.get(original_file_name="test3.txt")


        vsname = randstring()
        vs1 = VectorStore(name=vsname)
        vs1.save()
        vs1.files.set([t1])
        vs1.save()

        vsname = randstring()
        vs2 = VectorStore(name=vsname)
        vs2.save()
        vs2.files.set([t2,t3])
        vs2.save()

        aname = randstring()
        assistant = Assistant( name=aname)
        assistant.instructions = 'Here are instructions; be nice!'
        assistant.save();
        assistant.vector_stores.add(vs1)
        assistant.save();
        file_ids = assistant.file_ids()
        print(f"ASSISTANT FILE_IDS = {file_ids}")

        assert  assistant.files_ok()  , f"FILE_IDS_LOCAL = {file_ids} not equal to FILE_IDS_REMOTE "
        print(f"NOW ADD VS2")
        assistant.vector_stores.add(vs2)
        file_ids = assistant.file_ids()
        print(f"FILE_IDS IS NOW {file_ids}")
        assert assistant.files_ok() , 'FILES_IDS_LOCAL = {file_ids}'
        print(f"NOW SUBTRACT VS1")
        assistant.vector_stores.remove(vs1)
        file_ids = assistant.file_ids()
        print(f"FILE_IDS IS NOW {file_ids}")
        assert assistant.files_ok() , 'FILES_IDS_LOCAL = {file_ids}'

        assistant.vector_stores.remove(vs2)
        file_ids = assistant.file_ids()
        print(f"FILE_IDS SHOULD BE EMPTY : IS NOW {file_ids}")
        assert assistant.files_ok() , 'FILES_IDS_LOCAL = {file_ids}'

        vs1.delete();
        vs2.delete();
        t1.delete();
        t2.delete();
        t3.delete();
        assistant.delete();

    def test_create_and_delete_thread(self):
        import tiktoken


        url = reverse('admin:sidecar_openai_openaifile_changelist')  # use your app and model name
        response = self.client.get(url)
        print(f"RESPONSE = {response}")
        url = reverse('admin:sidecar_openai_openaifile_add')  # use your app and model name
        test_file1 = SimpleUploadedFile( "test1.txt", b"The dog was black\n", content_type="text/plain")
        self.client.post( url ,  {'file': test_file1}, follow=True)
        t1 = OpenAIFile.objects.get(original_file_name="test1.txt")
        test_file2 = SimpleUploadedFile( "test2.txt", b"The cat was white.\n", content_type="text/plain")
        self.client.post( url ,  {'file': test_file2}, follow=True)
        t2 = OpenAIFile.objects.get(original_file_name="test2.txt")

        test_file3 = SimpleUploadedFile( "test3.txt", b"The dog chased the cat \n", content_type="text/plain")
        self.client.post( url ,  {'file': test_file3}, follow=True)
        t3 = OpenAIFile.objects.get(original_file_name="test3.txt")


        vsname = randstring()
        vs1 = VectorStore(name=vsname)
        vs1.save()
        vs1.files.set([t1,t2,t3])
        vs1.save()
        aname = randstring()
        assistant = Assistant( name=aname)
        assistant.instructions = 'Here are instructions; be nice!'
        assistant.save();
        assistant.vector_stores.add(vs1)
        assistant.save();
        file_ids = assistant.file_ids()
        assistant_id = assistant.assistant_id
        print(f"ASSISTANT FILE_IDS = {file_ids}")
        assert  assistant.files_ok()  , f"FILE_IDS_LOCAL = {file_ids} not equal to FILE_IDS_REMOTE "
        print(f"ASSITANT REMOTE FILES OK")
        #client.beta.assistants.update(
        #    assistant_id=assistant_id,
        #    tool_resources={"file_search": {"vector_store_ids": [vector_store_id]}},
        #    )
        thread = client.beta.threads.create(); 
        thread_id = thread.id
        queries =  [ 'What color was the dog.',
                     'What color was the cat.',
                     'What did the dog do?',
                      'Please repeat the reply to the first request']
        encoding = tiktoken.encoding_for_model(model)
        for query in queries :
            openai.beta.threads.messages.create( thread_id=thread_id,  role="user", content=query)
            run = openai.beta.threads.runs.create( thread_id=thread_id, assistant_id=assistant_id)
            while True:
                run_status = openai.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
                if run_status.status == "completed":
                    break
                elif run_status.status == "failed":
                    raise Exception("Run failed.")
                else:
                    print("Waiting for completion...")
                    time.sleep(1)
            messages = openai.beta.threads.messages.list(thread_id=thread_id)
            i = 0;
            for msg in messages.data[::-1]:  # newest last
                i = i + 1 
                if msg.role == "assistant":
                    res = msg
            txt =   str( msg.content[0].text.value )
            tokens = encoding.encode(txt)
            print(f"RETGURN TOKENS = {len(tokens)} REPLY = {txt}")

        vs1.delete();
        t1.delete();
        t2.delete();
        t3.delete();
        assistant.delete();
