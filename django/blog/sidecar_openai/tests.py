from django.test import TestCase
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




class OpenAI(TestCase):
    def setUp( self ):
        User = get_user_model()
        self.admin_user = User.objects.create_superuser( username='admin', email='admin@example.com', password='adminpass')
        self.client.login(username='admin', password='adminpass')

    def test_create_and_delete_file_object(self):
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




    def test_create_and_delete_two_openai_file_objects(self):
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






    def test_create_and_delete_vector_store_object(self):
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


