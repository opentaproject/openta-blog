# Generated by Django 5.1.2 on 2024-11-15 08:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="comment",
            name="user",
        ),
    ]
