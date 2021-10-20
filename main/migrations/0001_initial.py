# Generated by Django 3.1.2 on 2021-10-20 07:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=10)),
                ('curriculum', models.CharField(max_length=20)),
                ('name', models.CharField(max_length=127)),
                ('description', models.CharField(blank=True, max_length=2048)),
                ('sks', models.PositiveSmallIntegerField()),
                ('term', models.PositiveSmallIntegerField()),
                ('prerequisites', models.CharField(blank=True, max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=63)),
                ('name', models.CharField(max_length=63)),
                ('npm', models.CharField(max_length=10)),
                ('faculty', models.CharField(max_length=63)),
                ('study_program', models.CharField(max_length=63)),
                ('educational_program', models.CharField(max_length=63)),
                ('role', models.CharField(max_length=63)),
                ('org_code', models.CharField(max_length=63)),
            ],
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField()),
                ('updated_at', models.DateTimeField()),
                ('academic_year', models.CharField(max_length=9)),
                ('semester', models.IntegerField(choices=[(1, 'Ganjil'), (2, 'Genap')])),
                ('content', models.TextField()),
                ('hate_speech_status', models.CharField(choices=[('WAITING', 'Waiting'), ('APPROVED', 'Approved'), ('REJECTED', 'Rejected')], max_length=20)),
                ('sentimen', models.PositiveSmallIntegerField(null=True)),
                ('is_anonym', models.BooleanField(default=False)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.course')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='main.profile')),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tag_name', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='ReviewTag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('review', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.review')),
                ('tag', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.tag')),
            ],
        ),
        migrations.CreateModel(
            name='ReviewLike',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('review', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.review')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.profile')),
            ],
        ),
        migrations.CreateModel(
            name='Bookmark',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.course')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.profile')),
            ],
        ),
    ]
