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
        print(f"RESPONSE = {response}")
        url = reverse('admin:sidecar_openai_openaifile_add')  # use your app and model name
        test_file = SimpleUploadedFile( "test.txt", b"file_content_here", content_type="text/plain")
        response3 = self.client.post( url ,  {'file': test_file}, follow=True)
        file_ids  = OpenAIFile.objects.all().values_list('file_id',flat=True)
        t = OpenAIFile.objects.get(original_file_name="test.txt")
        file_id = t.file_id
        try :
            aifile = client.files.retrieve(file_id)
            exists = True
        except openai.OpenAIError as e:
            exists = False
        assert exists , f"{file_id} Does not exist on server "
        path = t.path
        print(f"EXISTS = {exists} PATH={path} ")
        assert os.path.exists(path), f"LOCAL FILE PATH {path} DOES NOT EXIST"
        print(f"NOW DELETE THE FILE")
        t.delete();
        try :
            aifile = client.files.retrieve(file_id)
            exists = True
        except openai.OpenAIError as e:
            exists = False
        print(f"NOW EXISTS = {exists}")
        assert not exists, f"FILE {file_id} was not successfully deleted on the server"
        try :
            t = OpenAIFile.objects.get(original_file_name="test.txt")
            exists_locally = True
        except ObjectDoesNotExist as e :
            exists_locally = False
            print(f"OK! text.txt IS GONE  LOCALLY ")
        assert not exists_locally, f"File {file_id} still exists locally"
        assert not os.path.exists(path), f"LOCAL FILE PATH {path} DID NOT GET DELETED"



# Create your tests here.
