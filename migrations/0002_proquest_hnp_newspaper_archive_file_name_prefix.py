# Generated by Django 2.2.4 on 2019-08-16 02:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('context_text_proquest_hnp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='proquest_hnp_newspaper',
            name='archive_file_name_prefix',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
