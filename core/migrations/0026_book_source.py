# Generated by Django 3.2.6 on 2022-04-18 23:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0025_categoryposts'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='source',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]