# Generated by Django 4.1.5 on 2023-02-16 11:53

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("peaks", "0004_waypoint"),
    ]

    operations = [
        migrations.AlterField(
            model_name="waypoint",
            name="lat",
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="waypoint",
            name="lon",
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="waypoint",
            name="name",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name="waypoint",
            name="number",
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
