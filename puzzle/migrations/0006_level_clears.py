# Generated by Django 2.1 on 2018-08-23 07:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('puzzle', '0005_auto_20180821_2205'),
    ]

    operations = [
        migrations.AddField(
            model_name='level',
            name='clears',
            field=models.IntegerField(default=0),
        ),
    ]
