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

ITEMSPERPAGE = 20



def index(request, slug=None):
    # Default lat lon for map
    lat, lon = 45.5, 9.9
    mapmode = "alps"
    
    # Order by
    if request.GET.get('order') and request.GET.get('order') in ['neargtdist', '-neargtdist', 'name', '-name', 'ele', '-ele']:
        order = request.GET.get('order')
    else:
        order = '-ele'

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
    paginator = Paginator(allpeaks, ITEMSPERPAGE)
    
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

    # Pagination
    tours = Tour.objects.filter(peak=peak)
    paginator = Paginator(tours, ITEMSPERPAGE)

    try:
        page_number = int(request.GET.get('page'))
    except TypeError:
        # GET request without ?page=int
        page_number = 1

    page_obj = paginator.get_page(page_number)

    return render(request, "peaks/peak.html", {
        "peak": peak,
        "page_obj": page_obj,
    })


def profile(request, username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        raise Http404("User does not exist")

   
    tours = Tour.objects.filter(user=user).order_by("-timestamp")

    # Pagination
    paginator = Paginator(tours, ITEMSPERPAGE)

    try:
        page_number = int(request.GET.get('page'))
    except TypeError:
        # GET request without ?page=int
        page_number = 1

    page_obj = paginator.get_page(page_number)

    highest = Peak.objects.filter(tours__user=user).order_by('-ele').first
    gotlikes = user.likes
    gavelikes = Tour.objects.filter(likedby=user).count()

    return render(request, "peaks/profile.html", {
            "page_obj": page_obj,
            "title": f"Profile of {username}",
            "username": username,
            "counttours": tours.count(),
            "highest": highest,
            "gotlikes": gotlikes,
            "gavelikes": gavelikes,
        })


@login_required
def tour(request, id=None):
    if id:
        # All modes except new tour
        try:
            tour = Tour.objects.get(id=id)
        except (Tour.DoesNotExist, ValueError):
            raise Http404("Page not found")

        # Delete mode
        if request.method == "DELETE":
            print("delete")
            if tour.user == request.user:
                count, _ = tour.delete()
                print(f"Deleted {count} records (tours/waypoints)")
                if count >= 1:
                    return HttpResponse('Tour has been deleted', status=200)
                else:
                    # Not succesfull (request not valid)
                    return HttpResponse('Could not delete tour', status=404)
            else:
                print("Delete forbidden")
                # Forbidden
                return HttpResponse('Forbidden', status=403)

        
    # POST (edit or new tour)
    if request.method == "POST":
        if id:
            # Edit
            form = TourForm(request.POST, instance=tour)
        else:
            # New
            form = TourForm(request.POST)
        waypointformset = WaypointFormset(request.POST)
        
        if form.is_valid():
            # Get instance of tour without commiting to DB
            tourpost = form.save(commit=False)

            for tag in tourpost.tags.all():
                print(tag)

            try:
                # Edit tour
                user = tourpost.user
                
            except Tour.user.RelatedObjectDoesNotExist:
                # New tour
                oldwaypoints = []

            else:
                # Edit: Check if editing is allowed
                if tour.user != request.user or user != request.user:
                    return HttpResponse(status=400)
                oldwaypoints = list(tour.waypoints.all())
            
            tourpost.user = request.user

            # Commit new version to DB
            tourpost.save()

            # Save tags (many to many relationship)
            form.save_m2m()

            # Waypoints
            if waypointformset.is_valid():
                for wp in waypointformset.cleaned_data:
                    try:
                        lat = float(wp['lat'])
                        lon = float(wp['lon'])
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
                        waypoint.tour = tourpost
                        waypoint.save()

            # Delete any left over old waypoints
            for wp in oldwaypoints:
                wp.delete()

            # Redirect to the site of the tour
            return HttpResponseRedirect(reverse("showtour", kwargs={'id': tourpost.id}))
        else:
            print(form.errors)
            return HttpResponse("Invalid form", status=400)

    # PUT
    if request.method == "PUT":
        # Toggle like
        if not json.loads(request.body).get("toggle"):
            return HttpResponse(status=400)
        # Dont allow users to like their own tours
        if request.user == tour.user:
            return HttpResponse(status=403)
        
        # Toggle like
        if request.user in tour.likedby.all():
            tour.likedby.remove(request.user)
        else:
            tour.likedby.add(request.user)

        tour.save()
        return HttpResponse(status=200) 


    # GET
    if request.GET.get('new'):
        # New tour
        peakid = request.GET.get('new')
        try:
            peak = Peak.objects.get(id=peakid)
        except Peak.DoesNotExist:
            raise Http404("Page not found")
        return render(request, "peaks/tour.html",{
            "tourform": TourForm(initial={'peak': peakid}),
            "wpformset": WaypointFormset(queryset=Waypoint.objects.none()),
            "title": f"New tour on {peak.name}",
            "peak": peak,
        })

    elif id:
        # Edit mode
                
        if tour.user != request.user:
            return HttpResponse(status=400)

        return render(request, "peaks/tour.html",{
             "tourform": TourForm(instance=tour),
             "wpformset": WaypointFormset(queryset=Waypoint.objects.filter(tour=tour)),
             "title": f"Edit tour on {tour.peak.name}",
             "peak": tour.peak,
             "tourid": tour.id,
        })

    else:
        # Show latest tours
        tours = Tour.objects.all().order_by('-timestamp')[:ITEMSPERPAGE]

        return render(request, "peaks/tourlist.html", {
            "tours": tours,
        })
          


def showtour(request, id=None):
    if id:
        try:
            tour = Tour.objects.get(id=id)
        except Tour.DoesNotExist:
            raise Http404("Page not found")
        return render(request, "peaks/showtour.html", {
            "tour": tour
        })
    else:
        # Show latest tours
        tours = Tour.objects.all().order_by('-timestamp')[:20]

        return render(request, "peaks/tourlist.html", {
            "tours": tours,
        })

def waypoints(request, id):
    """Return waypoints als GeoJSON"""
    try:
        tour = Tour.objects.get(id=id)
    except Tour.DoesNotExist:
        raise Http404("Page not found")
    waypoints = tour.waypoints.all().order_by("number")

    return JsonResponse([wp.geojson() for wp in waypoints], safe=False)

def likes(request, id):
    try:
        tour = Tour.objects.get(id=id)
    except Tour.DoesNotExist:
        raise Http404("Page not found")

    # Return likes
    return JsonResponse({
        "liked": (request.user in tour.likedby.all()),
        "count": tour.likes,
    }, status=200)

def tag(request, slug):
    try:
        tag = Tag.objects.get(slug=slug)
    except Tag.DoesNotExist:
        raise Http404("Page not found")
    
    tours = Tour.objects.filter(tags=tag).order_by("-timestamp")
    highest = Peak.objects.filter(tours__tags=tag).order_by('-ele').first
    print(highest)

    # Pagination
    paginator = Paginator(tours, ITEMSPERPAGE)

    try:
        page_number = int(request.GET.get('page'))
    except TypeError:
        # GET request without ?page=int
        page_number = 1

    page_obj = paginator.get_page(page_number)


    return render(request, "peaks/profile.html", {
            "page_obj": page_obj,
            "title": f"Tag {tag.name}",
            "counttours": tours.count(),
            "highest": highest,
        })

def tags(request):
    tags = Tag.objects.all().order_by("name")

    return render(request, "peaks/tags.html", {
        "tags": tags,
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
