# Generated by Django 5.2.4 on 2025-07-16 08:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscription',
            name='plan',
            field=models.CharField(choices=[('basic', 'Basic Plan - £9.99/month'), ('premium', 'Premium Plan - £19.99/month'), ], max_length=20),
        ),
    ]
