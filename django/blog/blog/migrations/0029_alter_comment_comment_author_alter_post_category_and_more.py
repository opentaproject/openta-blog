# Generated by Django 5.1.2 on 2025-02-09 21:29

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0028_remove_filterkey_subdomain"),
    ]

    operations = [
        migrations.AlterField(
            model_name="comment",
            name="comment_author",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="comment_author",
                to="blog.visitor",
            ),
        ),
        migrations.AlterField(
            model_name="post",
            name="category",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="post",
                to="blog.category",
            ),
        ),
        migrations.AlterField(
            model_name="post",
            name="post_author",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="post",
                to="blog.visitor",
            ),
        ),
    ]
