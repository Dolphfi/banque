# Generated by Django 5.0.6 on 2024-11-25 21:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0006_client_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='email',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='client',
            name='password',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]