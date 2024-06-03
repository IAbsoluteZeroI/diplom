# Generated by Django 5.0.4 on 2024-06-03 20:22

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Camera',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('floor', models.CharField(max_length=5)),
                ('wing', models.CharField(max_length=6)),
                ('video_path', models.CharField(blank=True, default='', max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='EventHistory',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('type', models.CharField(max_length=3)),
                ('frame', models.IntegerField(default=0)),
                ('object', models.CharField(max_length=100)),
                ('from_place', models.CharField(max_length=100)),
                ('to_place', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Object',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='Place',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('description', models.CharField(blank=True, default='', max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='LineCounter',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('start_x', models.FloatField(default=0)),
                ('start_y', models.FloatField(default=0)),
                ('end_x', models.FloatField(default=0)),
                ('end_y', models.FloatField(default=0)),
                ('camera', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='line_counters', to='furniture_monitoring.camera')),
            ],
        ),
        migrations.CreateModel(
            name='ObjectsInPlace',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('quantity', models.IntegerField(default=0)),
                ('object', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='object', to='furniture_monitoring.object')),
                ('place', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='place', to='furniture_monitoring.place')),
            ],
        ),
        migrations.AddField(
            model_name='camera',
            name='place',
            field=models.ForeignKey(blank=True, default='', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='cameras', to='furniture_monitoring.place'),
        ),
    ]
