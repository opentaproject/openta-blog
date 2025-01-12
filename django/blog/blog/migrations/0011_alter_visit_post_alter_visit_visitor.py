# Generated by Django 5.1.2 on 2025-01-11 10:43

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0010_subdomain_category_hidden_alter_comment_post_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="visit",
            name="post",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="visit_post",
                to="blog.post",
            ),
        ),
        migrations.AlterField(
            model_name="visit",
            name="visitor",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="visit_visitor",
                to="blog.post",
            ),
        ),
    ]