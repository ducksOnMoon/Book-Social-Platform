# Generated by Django 3.2.6 on 2021-10-24 11:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_alter_book_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='about',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='about/'),
        ),
    ]