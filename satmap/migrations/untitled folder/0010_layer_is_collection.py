# Generated by Django 3.2.20 on 2023-08-23 22:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('satmap', '0009_alter_layer_palette'),
    ]

    operations = [
        migrations.AddField(
            model_name='layer',
            name='is_collection',
            field=models.BooleanField(default=True),
        ),
    ]
