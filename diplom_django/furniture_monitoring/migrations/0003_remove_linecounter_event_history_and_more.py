# Generated by Django 5.0.4 on 2024-05-13 18:09

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('furniture_monitoring', '0002_remove_linecounter_coord_left_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='linecounter',
            name='event_history',
        ),
        migrations.AddField(
            model_name='eventhistory',
            name='line_counter',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='event_histories', to='furniture_monitoring.linecounter'),
        ),
    ]