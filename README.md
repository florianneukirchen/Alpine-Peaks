# Alpine Peaks (CS50W Final Project)

Alpine Peaks is a web app about the peaks of the Alps, using python, django, and javascript. It is my final project of the online course [CS50W Web Programming with Python and JavaScript](https://www.edx.org/course/cs50s-web-programming-with-python-and-javascript) from Harvard / edx.

You can get information about all peaks higher than 1000 m, and users can add their tours.

## Distinctiveness and Complexity
- Django:
    - I had to write (and learn how to write) a [data migration](https://docs.djangoproject.com/en/4.1/howto/writing-migrations/) to get data of peaks into the database.
    - Use djangos [model forms](https://docs.djangoproject.com/en/4.1/topics/forms/modelforms/) to generate forms. 
    - Dynamically generate forms to add any number of waypoints to a tour using a [formset](https://docs.djangoproject.com/en/4.1/topics/forms/formsets/). When editing a tour, initialize the formset with existing waypoints. (Used references: [1](https://groups.google.com/g/django-users/c/Gk4H2ABEPyI), [2](https://stackoverflow.com/questions/61285171/initialize-a-formset), [3](https://stackoverflow.com/questions/1992152/django-initializing-a-formset-of-custom-forms-with-instances), [4](https://simpleit.rocks/python/django/dynamic-add-form-with-add-button-in-django-modelformset-template/) )
    - Use slugs for the urls.
    - Implement an API that returns coordinates as GeoJSON.
    - To get the 3 most dominant peaks of every region for the map, I use a [subquery](https://stackoverflow.com/questions/60478733/django-selecting-top-n-records-per-group-using-orm). This is *very* slow, therefore I implemented ...
    - ... caching for the GeoJSON API. The data is not changing anyway.
- Javascript:  
    - Get Wikipedia extract and thumbnail image (including image rights) with AJAX from [Wikipedia API](https://www.mediawiki.org/wiki/API:Main_page).
    - Use [Leaflet](https://leafletjs.com/) to show a map. 
    - Get peaks and waypoints with AJAX using my GeoJSON API and plot them on the map.
    - Implement adding waypoint markers with a click on the map and editing of the coordinates by dragging markers (the numbered markers are adapted from this [post](https://stackoverflow.com/questions/1992152/django-initializing-a-formset-of-custom-forms-with-instances)).
    - After learning jQuery I tried to use jQuery as much as possible.

- Data:
    - I used python and geopandas to clean and enrich the data originally downloaded from OpenStreetMap.

## Peak Data
The app requires data of the peaks of the Alps that can be downloaded into the working directory of the project with:

```wget https://www.dropbox.com/s/gk055ofbfswigwj/alps.geojson?dl=0 -O alps.geojson```

The data is © [OpenStreetMap](https://www.openstreetmap.org/copyright/en) and Florian Neukirchen under [Open Database License](https://www.openstreetmap.org/copyright/en).

The data was downloaded in [QGIS](https://www.qgis.org/) using the [QuickOSM](https://plugins.qgis.org/plugins/QuickOSM/) plugin (search for natural=peak). It was preprocessed in a Jupyter Notebook ([alpine_peaks.ipynb on GitHub](https://github.com/florianneukirchen/jupyter-notebooks/blob/main/alpine_peaks.ipynb)) with python and geopandas. In QGIS I added the nearest higher peak with my QGIS plugin [nearest greater](https://github.com/florianneukirchen/qgis_nearest_greater) - I wrote this plugin in the last months.


## Files



### peaks/migrations/0002_auto .... .py
This file is the [data migration](https://docs.djangoproject.com/en/4.1/howto/writing-migrations/) to load the peaks data into the database. It will fail if the file alps.geojson does not exist, you have to download the file first with:

```wget https://www.dropbox.com/s/gk055ofbfswigwj/alps.geojson?dl=0 -O alps.geojson```

The data migration reads the peaks data as json and saves it to the database. 