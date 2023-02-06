from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    pass


class Country(models.Model):
    name = models.CharField(max_length=15)
    peaks = models.ManyToManyField("Peak", related_name="countries")

class Area(models.Model):
    name = models.CharField(max_length=65)

class Peak(models.Model):
    # ID is not auto increment, I want to use OSM IDs
    id = models.IntegerField(primary_key=True)

    name = models.CharField(max_length=80)
    alias = models.CharField(max_length=30, null=True, blank=True)
    name_en = models.CharField(max_length=50, null=True, blank=True)
    name_de = models.CharField(max_length=50, null=True, blank=True)
    name_fr = models.CharField(max_length=50, null=True, blank=True)
    name_it = models.CharField(max_length=50, null=True, blank=True)
    name_sl = models.CharField(max_length=50, null=True, blank=True)
    name_ch = models.CharField(max_length=50, null=True, blank=True)
    name_de_AT = models.CharField(max_length=50, null=True, blank=True)
    name_de_DE = models.CharField(max_length=50, null=True, blank=True)
    alt_name = models.CharField(max_length=70, null=True, blank=True)

    lat = models.FloatField()
    lon = models.FloatField()

    area = models.ForeignKey("Area", on_delete=models.CASCADE, related_name="peaks", blank=True)

    prominence = models.IntegerField(null=True, blank=True)

    # The output of the nearest greater QGIS Plugin
    neargt = models.ForeignKey("Peak", on_delete=models.CASCADE, related_name="nearestlower", blank=True, null=True)
    neargtdelta = models.FloatField(null=True)
    neargtdist = models.FloatField(null=True)

    class Meta:
        indexes = [
            models.Index(fields=['name', 'alias', 'name_en', 'name_de', 'name_fr', 'name_it', 'name_sl', 'name_ch', 'name_de_AT', 'name_de_DE', 'alt_name']),
            models.Index(fields=['area']),
        ]


class Tour(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="tours")
    text = models.TextField(blank=True)
    date = models.DateField(blank=True)
    heading = models.CharField(max_length=255, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    likedby = models.ManyToManyField("User", related_name="liked_tours", blank=True, default="")

    @property
    def likes_count(self):
        return self.likedby.all().count()