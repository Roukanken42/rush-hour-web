# Generated by Django 2.1 on 2018-08-21 20:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('puzzle', '0004_clear'),
    ]

    operations = [
        migrations.AddField(
            model_name='level',
            name='height',
            field=models.IntegerField(default=310),
        ),
        migrations.AddField(
            model_name='level',
            name='width',
            field=models.IntegerField(default=310),
        ),
    ]
