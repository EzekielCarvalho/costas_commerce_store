# Generated by Django 2.2.13 on 2021-11-05 17:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0017_auto_20211105_2231'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='name',
            field=models.CharField(default='uncategorized', max_length=255),
            preserve_default=False,
        ),
    ]
