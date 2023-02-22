# Alpine Peaks (CS50W Final Project)

Alpine Peaks is a web app about the peaks of the Alps, using python, [django](https://www.djangoproject.com/), javascript, and [bootstrap](https://getbootstrap.com/). It is my final project of the online course [CS50W Web Programming with Python and JavaScript](https://www.edx.org/course/cs50s-web-programming-with-python-and-javascript) from Harvard / edx.

The app shows information about all peaks of the Alps that are higher than 1000 m, including a map and an image and extract from Wikipedia. Users can add their tours with description, grade, tags and waypoints.

![]()

## Distinctiveness and Complexity
- Django:
    - Use a [data migration](https://docs.djangoproject.com/en/4.1/howto/writing-migrations/) to get data of peaks into the database.
    - Use djangos [model forms](https://docs.djangoproject.com/en/4.1/topics/forms/modelforms/) to generate forms and create instances of models. 
    - Dynamically generate forms to add any number of waypoints to a tour using a [formset](https://docs.djangoproject.com/en/4.1/topics/forms/formsets/). When editing a tour, initialize the formset with existing waypoints. (Used references: [1](https://groups.google.com/g/django-users/c/Gk4H2ABEPyI), [2](https://stackoverflow.com/questions/61285171/initialize-a-formset), [3](https://stackoverflow.com/questions/1992152/django-initializing-a-formset-of-custom-forms-with-instances), [4](https://simpleit.rocks/python/django/dynamic-add-form-with-add-button-in-django-modelformset-template/) )
    - Use slugs for the urls.
    - Implement an API that returns coordinates as GeoJSON.
    - To get the 3 most dominant peaks of every region for the map, I use a [subquery](https://stackoverflow.com/questions/60478733/django-selecting-top-n-records-per-group-using-orm). This is *very* slow, therefore I implemented ...
    - ... caching for the GeoJSON API. The data is not changing anyway.
- Javascript:  
    - Get Wikipedia extract and thumbnail image (including image rights) with AJAX from [Wikipedia API](https://www.mediawiki.org/wiki/API:Main_page).
    - Use [Leaflet](https://leafletjs.com/) to show a map. 
    - Get peaks and waypoints with AJAX using my GeoJSON API and plot them on the map.
    - Implement adding waypoint markers with a click on the map and editing of the coordinates by dragging markers (the numbered marker icons are adapted from this [post](https://stackoverflow.com/questions/1992152/django-initializing-a-formset-of-custom-forms-with-instances)).
    - After learning jQuery I tried to use jQuery as much as possible.

- Data:
    - I used python and [geopandas](https://geopandas.org/en/stable/) to clean and enrich the raw data originally downloaded from OpenStreetMap.


## Requirements
- django (tested with django 4.1.5)
- Download peak data, see next section


## <a name="run"></a>Run the Application
- Install Django
- cd into the directory of the app (containing manage.py)
- Download peak data with:

```
wget https://www.dropbox.com/s/gk055ofbfswigwj/alps.geojson?dl=0 -O alps.geojson
```

- Create database and load initial data into database with:

```
python manage.py makemigrations
python manage.py migrate
``` 

- You can now remove alps.geojson:
```
rm alps.geojson
``` 

- Start app/webserver with:
```
python manage.py runserver
``` 


## About the Peak Data
The app requires data of the peaks of the Alps that must be downloaded into the working directory (see [Run the Application](#run) above) before running the app for the first time.

The peak data is © [OpenStreetMap](https://www.openstreetmap.org/copyright/en) and Florian Neukirchen under [Open Database License](https://www.openstreetmap.org/copyright/en).

The data was originally downloaded in [QGIS](https://www.qgis.org/) using the [QuickOSM](https://plugins.qgis.org/plugins/QuickOSM/) plugin (search for natural=peak). It was preprocessed in a Jupyter Notebook ([alpine_peaks.ipynb on GitHub](https://github.com/florianneukirchen/jupyter-notebooks/blob/main/alpine_peaks.ipynb)) with python and geopandas. In QGIS I added the nearest higher peak with my QGIS plugin [nearest greater](https://github.com/florianneukirchen/qgis_nearest_greater) – I wrote this plugin in the last months.




## Files

### peaks/models.py
Contains the models used by the app:
- User
- Peak 
  - Contains all the data extracted from OpenStreetMap including coordinates, elevation, names in different languages, etc.)
  - The function ``geojson()`` returns the peak as GeoJSON feature.
  - The property ``likes`` returns the sum of all likes of tours to the peak. 
  - Relation to the models Country, Region, Tour.
- Country
- Region
- Tour
  - Users can post tours to any peak; with heading, description, grade, date, tags, and waypoints.
  - Tours can be liked by other users.
- Waypoint
  - Tours can have waypoints (with latitude, longitude and optional name).
  - The function ``geojson()`` returns the waypoint as GeoJSON feature.
- Tag (for Tours)
- Grade (for Tours)

### peaks/forms.py
Contains the forms used by the app:
- OrderSelect (used to select the order on the index view)
- WaypointForm (model form based on Waypoint model, used in WaypointFormset)
- WaypointFormset (formset used in the view for editing/creating tours)
- TourForm (model form based on Tour model, used in the view for editing/creating tours)


### peaks/migrations/0002_auto .... .py
This file is the [data migration](https://docs.djangoproject.com/en/4.1/howto/writing-migrations/) to load the peaks data into the database. It will fail if the file alps.geojson does not exist. As already mentioned,  you have to download the file first with:

```
wget https://www.dropbox.com/s/gk055ofbfswigwj/alps.geojson?dl=0 -O alps.geojson
```

The data migration reads the peaks data as json and saves it to the database. 

### peaks/migrations/0009_auto.... .py
Another data migration to add some tags and grades (of mountain tours) to the database.

### peaks/views.py
The view functions used by the app. The most important views are:
- index()
    - lists peaks using pagination 
    - used for: 
      - the main route, listing all peaks of the alps
      - the region and country routes (url with slug)
      - search (with a GET request with ``?q=<searchstring>``)
- peak()
    - Show detailed information of a peak
    - List tours using pagination
- tour()
    - Create new tours, edit tours, delete tours, like tours.
    - Login required
    - A GET request renders the form
      - ... for a new tour, if the peak id is passed with ``?new=<peakid>``
      - ... to edit an existing tour for urls like ``edit/<tourid>``
    - A POST request saves the data from the form to the database.
    - A DELETE request deletes a tour.
    - A PUT request is used to like a tour.
    - Uses the form TourForm and the formset WaypointFormset
- showtour()
    - Show the details of a tour
- profile()
    - Show user profile
    - List tours using pagination
- jsonapi()
    - Returns peaks as JSON features
    - Used with AJAX to plot peaks on the map
    - With slug: all peaks of a region
    - Without slug: The 3 most dominant peaks of each region (the algorithm uses a subquery and is very slow)
    - Uses caching
- waypoints()
    - Returns waypoints of a tour as GeoJSON to plot them on the map using AJAX.
- likes()
    - Update the likes of a tour after toggling the like.
- tag()
    - List tours with a given tag using pagination.
- tags()
    - List all tags.
- regionlist()
    - List all regions and countries.

### Templates in /peaks/templates/peaks
- layout.html (base layout used by all templates)
- index.html (used by index view)
- peak.html (used by peak view)
- tour.html (used by tour view to edit/create tours)
- showtour.html (used by showtour view)
- tourlist.html (used by showtour view to list recent tours)
- profile.html (used by profile and tags views)
- regions.html (used by regionlist view)
- (login.html and register.html are adapted from the problem sets).

### Javascript: /peaks/static/peaks/peaks.js
- Leaflet Map:
  - Show map with 2 different base maps.
  - Get peaks of mountain region with AJAX from my GeoJSON API and add them to the map as GeoJSON layer.
  - Same for dominant peaks of the Alps (3 prominent peaks for every regions).
  - Add tooltips and click events for these peak markers. 
  - Tour view: Get existing waypoints with AJAX from my GeoJSON API and add them to the map as GeoJSON layer.
- Edit waypoints: 
  - Add waypoints by clicking on the map.
  - This dynamically adds a form within the waypoints formset.
  - Waypoint markers can be dragged to a new position, the coordinates are updated in the form.
  - Allow to delete the last waypoint.
- Wikipedia API (with AJAX):
  - Search for Wikipedia article with the name of the peak.
  - Get the main image of the article, including image rights.
  - Get an extract of the article.   
- Handle click events etc.:
  - Toggle likes,
  - changes of the "order by" dropdown reload the page accordingly,
  - activate tooltips (used for tour grades),
  - delete tour with DELETE request.


### More files
- /peaks/urls.py (definition of url patterns)
- /static/peaks/peaks.css (custom css in addition to bootstrap)
- Icons:
  - favicon.ico
  - mountain.svg (marker icon on maps)
  - mountain-grey.svg (marker icon on maps)
  - wpmarker.png (marker icon for waypoints on maps)

## Limitation
For minor peaks, the article and image fetched from Wikipedia may not at all be related to the peak. 
