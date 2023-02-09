# Alpine Peaks (CS50W Final Project)

Alpine Peaks is a web app about the peaks of the Alps, using python, django, and javascript. It is my final project of the online course [CS50W Web Programming with Python and JavaScript](https://www.edx.org/course/cs50s-web-programming-with-python-and-javascript) from Harvard / edx.

You can get information about all peaks higher than 1000 m, and users can add their tours.

## Distinctiveness and Complexity
- Django:
    - I had to write (and learn how to write) a data migration to get data from OpenStreetMap into the database.
    - I use slugs for the urls (and learned how to do so).
    - Implement an API that returns coordinates as GeoJSON.
- Javascript:
    - After learning jQuery I tried to use jQuery as much as possible.
    - Get Wikipedia extract and thumbnail image (including image rights) with AJAX from Wikipedia API.
    - Use [Leaflet](https://leafletjs.com/) to show a map. 

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