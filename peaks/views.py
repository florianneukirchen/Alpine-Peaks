from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from django.http import HttpResponse, HttpResponseRedirect, Http404, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.db.models import OuterRef, Subquery
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.urls import reverse
import json

from .models import *
from .forms import *

PEAKSPERPAGE = 50



def index(request, slug=None):
    # Default lat lon for map
    lat, lon = 45.5, 9.9
    mapmode = "alps"
    
    # Order by
    order = '-ele'
    if request.GET.get('order') and request.GET.get('order') in ['neargtdist', '-neargtdist', 'name', '-name', 'ele', '-ele']:
        order = request.GET.get('order')

    # Search
    if request.GET.get('q'):
        query = request.GET.get('q')
        # Chain queries with "or" 
        # case insensitive contains: __icontains 
        allpeaks = (
            Peak.objects.filter(name__icontains=query) |
            Peak.objects.filter(alias__icontains=query) |
            Peak.objects.filter(name_en__icontains=query) |
            Peak.objects.filter(name_de__icontains=query) |
            Peak.objects.filter(name_fr__icontains=query) |
            Peak.objects.filter(name_it__icontains=query) |
            Peak.objects.filter(name_sl__icontains=query) |
            Peak.objects.filter(name_ch__icontains=query) |
            Peak.objects.filter(name_de_AT__icontains=query) |
            Peak.objects.filter(name_de_DE__icontains=query) |
            Peak.objects.filter(alt_name__icontains=query) |
            Peak.objects.filter(region__name__icontains=query)
            ).order_by(order)
        title = f"Search: {query}"
    
    # Region / Country
    elif slug:
        if Region.objects.filter(slug=slug).exists():
            region = Region.objects.get(slug=slug)
            allpeaks = Peak.objects.filter(region=region).order_by(order)   
            title = f"Peaks of {region.name}"
            # Get lat lon of highest peak 
            highest = Peak.objects.filter(region=region).order_by('-ele').first()
            lat = highest.lat
            lon = highest.lon
            mapmode = "region"

        elif Country.objects.filter(slug=slug).exists():
            country = Country.objects.get(slug=slug)
            allpeaks = Peak.objects.filter(countries=country).order_by(order) 
            title = f"Peaks of {country.name}"
        

    # Index (all peaks)
    else:
        allpeaks = Peak.objects.all().order_by(order)   
        title = "Peaks of the Alps"

    # Pagination    
    paginator = Paginator(allpeaks, PEAKSPERPAGE)
    
    try:
        page_number = int(request.GET.get('page'))
    except TypeError:
        # GET request without ?page=int
        page_number = 1
    
    page_obj = paginator.get_page(page_number)
    
    return render(request, "peaks/index.html", {
        "page_obj": page_obj,
        "title": title,
        "selectorder" : OrderSelect(initial={'order': order}),
        "lat": lat,
        "lon": lon,
        "regionslug": slug,
        "mapmode": mapmode
        })


@cache_page(None)
def jsonapi(request, slug=None):
    if slug:
        try:
            region = Region.objects.get(slug=slug)
        except Region.DoesNotExist:
            raise Http404("Page not found")
        allpeaks = region.peaks.all().order_by("-ele")
    else:
        # Use subquery to get n peaks with greatest neargtdist per region
        # Note: this is slow and should be cached
        n = 3
        top_peaks = Peak.objects.filter(region=OuterRef('region')).order_by('-neargtdist')[:n]
        allpeaks = Peak.objects.filter(id__in=Subquery(top_peaks.values('id')))

    return JsonResponse([peak.geojson() for peak in allpeaks], safe=False)


def regionlist(request):
    regions = Region.objects.all().order_by("name")
    countries = Country.objects.all().order_by("name")

    return render(request, "peaks/regions.html", {
        "regions": regions,
        "countries": countries,
    })


def peak(request, slug):
    try:
        peak = Peak.objects.get(slug=slug)
    except Peak.DoesNotExist:
        raise Http404("Page not found")

    return render(request, "peaks/peak.html", {
        "peak": peak,
    })


def profile(request, username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        raise Http404("User does not exist")

   
    tours = Tour.objects.filter(user=user).order_by("-timestamp")
    paginator = Paginator(tours, 20)

    try:
        page_number = int(request.GET.get('page'))
    except TypeError:
        # GET request without ?page=int
        page_number = 1

    page_obj = paginator.get_page(page_number)

    highest = Peak.objects.filter(tours__user=user).order_by('-ele').first

    return render(request, "peaks/profile.html", {
            "page_obj": page_obj,
            "title": username,
            "username": username,
            "counttours": tours.count(),
            "highest": highest,
        })


@login_required
def tour(request):
    if request.method == "POST":
        form = TourForm(request.POST)
        waypointformset = WaypointFormset(request.POST)
        print(waypointformset)

        if form.is_valid():
            # Get instance of tour without commiting to DB
            tour = form.save(commit=False)

            try:
                # Edit tour
                user = tour.user
                
            except Tour.user.RelatedObjectDoesNotExist:
                # New tour
                oldwaypoints = []

            else:
                # Edit: Check if editing is allowed
                try:
                    oldversion = Tour.objects.get(id=tour.id)
                except Tour.DoesNotExist:
                    return HttpResponse(status=400)
                if oldversion.user != request.user or user != request.user:
                    return HttpResponse(status=400)
                oldwaypoints = list(oldversion.waypoints.all())
            
            tour.user = request.user

            # Commit to DB
            tour.save()

            # Waypoints
            if waypointformset.cleaned_data is not None:
                for wp in waypointformset.cleaned_data:
                    print(wp)

                    try:
                        lat = int(wp['lat'])
                        lon = int(wp['lon'])
                        number = int(wp['number'])
                    except (ValueError, TypeError, KeyError):
                        # Ignore invalid data and empty forms
                        pass
                    else:
                        if len(oldwaypoints) > 0:
                            waypoint = oldwaypoints.pop()
                        else:
                            waypoint = Waypoint()
                        waypoint.number = number
                        waypoint.lat = lat
                        waypoint.lon = lon
                        waypoint.name = wp['name']
                        waypoint.tour = tour
                        waypoint.save()
                        print(waypoint)

            # Delete any left over old waypoints
            for wp in oldwaypoints:
                wp.delete()

            # Redirect to the site of the tour
            return HttpResponseRedirect(reverse("showtour", kwargs={'id': tour.id}))
        else:
            print(form.errors)
            return HttpResponse("Invalid form", status=400)

    # GET
    if request.GET.get('new'):
        peakid = request.GET.get('new')
        try:
            peak = Peak.objects.get(id=peakid)
        except Peak.DoesNotExist:
            raise Http404("Page not found")
        return render(request, "peaks/tour.html",{
            "tourform": TourForm(initial={'peak': peakid}),
            "title": f"New tour on {peak.name}",
            "peak": peak,
        })

    elif request.GET.get('edit'):
        try:
            tour = Tour.objects.get(id=int(request.GET.get('edit')))
        except (Tour.DoesNotExist, ValueError):
            raise Http404("Page not found")

                
        if tour.user != request.user:
            return HttpResponse(status=400)


        return render(request, "peaks/tour.html",{
             "tourform": TourForm(instance=tour),
             "title": f"Edit tour on {tour.peak.name}",
             "peak": tour.peak,
        })

    else:
        # Show latest tours
        tours = Tour.objects.all().order_by('-timestamp')[:20]

        return render(request, "peaks/tourlist.html", {
            "tours": tours,
        })
          


def showtour(request, id):
    try:
        tour = Tour.objects.get(id=id)
    except Tour.DoesNotExist:
        raise Http404("Page not found")
    return render(request, "peaks/showtour.html", {
        "tour": tour
    })

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "peaks/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "peaks/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "peaks/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "peaks/register.html")
