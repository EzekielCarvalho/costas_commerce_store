# Generated by Django 2.2.13 on 2021-11-05 05:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_auto_20211105_1039'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
