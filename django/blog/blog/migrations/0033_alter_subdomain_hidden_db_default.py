# Generated manually to ensure PostgreSQL applies a database-level default.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0032_subdomain_hidden"),
    ]

    operations = [
        migrations.AlterField(
            model_name="subdomain",
            name="hidden",
            field=models.BooleanField(db_default=True, default=True),
        ),
    ]
