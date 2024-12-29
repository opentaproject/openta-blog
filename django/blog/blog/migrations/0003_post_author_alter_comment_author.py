# Generated by Django 5.1.2 on 2024-12-29 11:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0002_remove_comment_user"),
    ]

    operations = [
        migrations.AddField(
            model_name="post",
            name="author",
            field=models.CharField(default="", max_length=60),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="comment",
            name="author",
            field=models.CharField(blank=True, default="", max_length=60),
        ),
    ]