# Generated by Django 2.2.4 on 2019-08-17 01:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('context_text_proquest_hnp', '0003_auto_20190817_0019'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='proquest_hnp_object_type',
            name='raw_value_2',
        ),
        migrations.RemoveField(
            model_name='proquest_hnp_object_type',
            name='raw_value_3',
        ),
        migrations.RemoveField(
            model_name='proquest_hnp_object_type',
            name='raw_value_4',
        ),
        migrations.RemoveField(
            model_name='proquest_hnp_object_type',
            name='raw_value_5',
        ),
        migrations.CreateModel(
            name='Proquest_HNP_Object_Type_Raw_Value',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('raw_value', models.TextField()),
                ('proquest_hnp_object_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='raw_value_set', to='context_text_proquest_hnp.Proquest_HNP_Object_Type')),
            ],
        ),
    ]
