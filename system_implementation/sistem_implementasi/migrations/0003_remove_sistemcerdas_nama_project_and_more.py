# Generated by Django 5.0.4 on 2024-06-28 08:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sistem_implementasi', '0002_sistemcerdas_nama_project'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sistemcerdas',
            name='nama_project',
        ),
        migrations.AddField(
            model_name='sistemcerdas',
            name='nama_sistem_cerdas',
            field=models.CharField(default='system_implementation', max_length=255),
        ),
    ]
