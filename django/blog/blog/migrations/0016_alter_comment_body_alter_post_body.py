# Generated by Django 5.1.2 on 2025-01-12 21:53

import django_ckeditor_5.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0015_remove_post_author"),
    ]

    operations = [
        migrations.AlterField(
            model_name="comment",
            name="body",
            field=django_ckeditor_5.fields.CKEditor5Field(verbose_name="Comment Body"),
        ),
        migrations.AlterField(
            model_name="post",
            name="body",
            field=django_ckeditor_5.fields.CKEditor5Field(verbose_name="Post Body "),
        ),
    ]
