# Generated by Django 5.1.2 on 2025-01-12 20:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0014_remove_comment_author"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="post",
            name="author",
        ),
    ]
