# Generated by Django 2.2.13 on 2021-11-03 14:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_auto_20211031_1140'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
