# Generated by Django 5.1.2 on 2025-01-31 21:51

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0023_visitor_alias"),
    ]

    operations = [
        migrations.AddField(
            model_name="filterkey",
            name="subdomain",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="filterkey",
                to="blog.subdomain",
            ),
        ),
    ]
