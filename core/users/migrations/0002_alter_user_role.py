# Generated by Django 5.2.1 on 2025-05-24 10:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(choices=[('admin', 'Admin'), ('company', 'Company'), ('volunteer', 'Volunteer')], default='volunteer', max_length=20),
        ),
    ]
