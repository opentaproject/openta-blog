from django.test import TestCase
from sidecar_openai.models import OpenAIFile, VectorStore, Assistant
from django.contrib.auth import get_user_model
from django.urls import reverse

# python manage.py test sidecar_openai.tests


class OpenAI(TestCase):
    def setUp( self ):
        User = get_user_model()
        self.admin_user = User.objects.create_superuser( username='admin', email='admin@example.com', password='adminpass')
        self.client.login(username='admin', password='adminpass')

    def test_create_model_in_admin(self):
        #o = OpenAIFile.objects.create(file="testdir/txt1.txt")
        url = reverse('admin:sidecar_openai_openaifile_changelist')  # use your app and model name
        response = self.client.get(url)
        print(f"RESPONSE = {response}")
        #self.assertEqual(response.status_code, 200)
        # Now POST data to create a new instance
        #response = self.client.post(url, {
        #    'field1': 'value1',
        #    'field2': 'value2',
        #    # ... include all required fields
        # })

    def test1(self) :
        #OpenAIFile.objects.create(file="testdir/txt3.txt")
        files = OpenAIFile.objects.all()
        print(f"FILES = {files}")

# Create your tests here.
