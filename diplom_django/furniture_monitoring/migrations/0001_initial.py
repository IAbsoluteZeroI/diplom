# Generated by Django 5.0.4 on 2024-05-13 17:17

import django.contrib.postgres.fields
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
            ],
        ),
        migrations.CreateModel(
            name='EventHistory',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('type', models.CharField(choices=[('in', 'in'), ('out', 'out')], max_length=3)),
                ('date', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='Object',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='ObjectsInPlace',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('chair', models.IntegerField()),
                ('person', models.IntegerField()),
                ('interactive_whiteboard', models.IntegerField()),
                ('keyboard', models.IntegerField()),
                ('monitor', models.IntegerField()),
                ('pc', models.IntegerField()),
                ('table', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='LineCounter',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('coord_left', django.contrib.postgres.fields.ArrayField(base_field=models.FloatField(), size=2)),
                ('coord_right', django.contrib.postgres.fields.ArrayField(base_field=models.FloatField(), size=2)),
                ('camera', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='line_counters', to='furniture_monitoring.camera')),
                ('event_history', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='event_histories', to='furniture_monitoring.eventhistory')),
                ('related_line_counter', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='related_line_counters', to='furniture_monitoring.linecounter')),
            ],
        ),
        migrations.AddField(
            model_name='eventhistory',
            name='object',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='event_objects', to='furniture_monitoring.object'),
        ),
        migrations.CreateModel(
            name='Place',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('place_objects', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='places', to='furniture_monitoring.objectsinplace')),
            ],
        ),
        migrations.AddField(
            model_name='camera',
            name='place',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cameras', to='furniture_monitoring.place'),
        ),
    ]
