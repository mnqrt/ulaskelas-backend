# Generated by Django 3.1.2 on 2021-11-08 02:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='tags',
            field=models.ManyToManyField(blank=True, related_name='courses', to='main.Tag'),
        ),
    ]
