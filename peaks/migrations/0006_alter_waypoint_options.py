# Generated by Django 4.1.5 on 2023-02-19 14:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('peaks', '0005_alter_waypoint_lat_alter_waypoint_lon_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='waypoint',
            options={'ordering': ['number']},
        ),
    ]
