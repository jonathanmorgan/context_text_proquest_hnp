# Generated by Django 2.2.4 on 2019-08-17 02:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('context_text_proquest_hnp', '0004_auto_20190817_0118'),
    ]

    operations = [
        migrations.AlterField(
            model_name='proquest_hnp_object_type',
            name='slug',
            field=models.SlugField(),
        ),
    ]
