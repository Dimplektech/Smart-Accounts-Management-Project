# Generated by Django 5.1.11 on 2025-07-09 07:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0008_recurringtransaction_is_active'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='account_number',
            field=models.CharField(blank=True, max_length=20, unique=True),
        ),
    ]
