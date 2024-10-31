import psycopg2
from psycopg2 import sql
from django.core.management import call_command
import os
import django
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from urllib.parse import urljoin



def create_database_if_not_exists(db_name, host,user , password , superuser, superuser_password ) :
    #host = settings.PGHOST
    #password = settings.PGPASSWORD
    #user=settings.PGUSER
    port = 5432
    # Connect to the default 'postgres' database
    conn = psycopg2.connect(dbname="postgres", user=user, password=password, host=host, port=port)
    conn.autocommit = True  # Enable auto-commit mode
    cursor = conn.cursor()
    
    # Check if the database exists
    cursor.execute(sql.SQL("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s"), [db_name])
    exists = cursor.fetchone()
    
    if not exists:
        # Database does not exist, so create it
        cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db_name)))
        print(f"Database '{db_name}' created successfully.")
        # Close the connection
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', '.settings')
        django.setup()
        cursor.close()
        conn.close()
        call_command( 'makemigrations' , 'users' )
        call_command( 'makemigrations' , 'blog' );
        call_command( 'migrate'  )
        call_command( 'createsuperuser','--noinput')


class CustomStorage(FileSystemStorage):
    location = os.path.join(settings.MEDIA_ROOT, "django_ckeditor_5")
    print(f"LOCATION1 = {location}")
    location = '/subdomain-data/openta-blog/media/django_ckeditor_5'
    print(f"LOCATION2 = {location}")
    base_url = urljoin(settings.MEDIA_URL, "django_ckeditor_5/")
    base_url = "/media/django_ckeditor_5/"
