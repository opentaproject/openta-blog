# Generated by Django 5.1.2 on 2025-01-13 22:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0020_alter_visitor_name"),
    ]

    operations = [
        migrations.AlterField(
            model_name="filterkey",
            name="name",
            field=models.CharField(max_length=120),
        ),
    ]
