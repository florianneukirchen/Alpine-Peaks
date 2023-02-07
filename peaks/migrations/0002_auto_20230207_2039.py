# Generated by Django 4.1.5 on 2023-02-07 20:39

# python manage.py makemigrations peaks --empty

from django.db import migrations
from django.db import IntegrityError
from django.utils.text import slugify
import os
import sys
import json

def load_peak_data(apps, schema_editor):
    Peak = apps.get_model("peaks", "Peak")
    Region = apps.get_model("peaks", "Region")
    Country = apps.get_model("peaks", "Country")

    # Countries
    countries = [
        'Austria',
        'France',
        'Germany',
        'Italy',
        'Liechtenstein',
        'Monaco',
        'Slovenia',
        'Switzerland',
        ]
    
    for c in countries:
        slug = slugify(c)
        country = Country(name=c, slug=slug)
        country.save()

    # Load peak data

    # Does file exist?
    if not os.path.exists("alps.geojson"):
        if os.path.exists("alps.geojson?dl=0"):
            os.rename("alps.geojson?dl=0", "alps.geojson")
        else:
            print("\nError: Data file not found. Please download with:")
            print("wget https://www.dropbox.com/s/gk055ofbfswigwj/alps.geojson?dl=0 -O alps.geojson")
            sys.exit(1)
    
    with open("alps.geojson") as f:
        data = json.load(f)

    # Create a set of all regions
    regions = {f['properties']['mountain_area'] for f in data['features']}
    
    # And save regions to DB
    for r in regions:
        # (We have None in regions)
        if r:
            slug = slugify(r)
            region = Region(name=r, slug=slug)
            region.save()
        
    # Save peaks
    print("Load peak data to DB...")
    for f in data['features']:
        prop = f['properties']
        id = prop.get('full_id')
        # OSM ID is in the form of 'n9975715157'
        # with n for node (= point)
        id = int(id[1:])

        prominence = prop.get('prominence')
        if prominence:
            prominence = int(prominence)
        
        neargtdelta = prop.get('neargtdelta')
        if neargtdelta:
            neargtdelta = float(neargtdelta)
        
        neargtdist = prop.get('neargtdist')
        if neargtdist:
            neargtdist = float(neargtdist) / 1000
        
        kwars = {
            'id':  id,
            'name': prop.get('name'),
            'alias': prop.get('alias'),
            'name_en': prop.get('name_en'),
            'name_de': prop.get('name_de'),
            'name_fr': prop.get('name_fr'),
            'name_it': prop.get('name_it'),
            'name_sl': prop.get('name_sl'),
            'name_ch': prop.get('name_ch'),
            'name_de_AT': prop.get('name_de_AT'),
            'name_de_DE': prop.get('name_de_DE'),
            'alt_name': prop.get('alt_name'),
            'prominence': prominence,
            'neargtdelta': neargtdelta,
            'neargtdist': neargtdist,
            'ele': float(prop.get('ele')),
            'lat': float(prop.get('lat')),
            'lon': float(prop.get('lon')),
        }
        
        peak = Peak(**kwars)

        region = prop.get('mountain_area')
        if region:
            peak.region = Region.objects.get(name=region)


        peak.save()

        for c in countries:
            if prop.get(c):
                country = Country.objects.get(name=c)
                country.peaks.add(peak)
                country.save()

    # Add nearestgt
    print("Add nearest higher peak...")
    for f in data['features']:
        prop = f['properties']
        id = prop.get('full_id')
        id = int(id[1:])

        neargtname = prop.get('neargtname') 

        if neargtname:
            neargtname = int(neargtname[1:])
            peak = Peak.objects.get(id=id)
            peak.neargt = Peak.objects.get(id=neargtname)
            peak.save()

    # Add slug, starting with prominent peaks
    print("Add slug...")
    for peak in Peak.objects.all().order_by("-ele"):
        i = 1
        sluggy = slugify(peak.name)
        slug = sluggy

        # Make sure it is unique
        while Peak.objects.filter(slug=slug).exists():
            i = i + 1
            slug = f"{sluggy}-{i}"
        peak.slug = slug
        peak.save()




class Migration(migrations.Migration):
    dependencies = [
        ("peaks", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(load_peak_data),
    ]