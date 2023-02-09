from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, Http404, JsonResponse
from django.core.paginator import Paginator
from django.urls import reverse
import json

from .models import *

PEAKSPERPAGE = 50



def index(request):
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
            ).order_by("-ele")
        title = f"Search: {query}"
    else:
        allpeaks = Peak.objects.all().order_by("ele")   
        title = "Peaks of the Alps"

    paginator = Paginator(allpeaks, PEAKSPERPAGE)
    
    try:
        page_number = int(request.GET.get('page'))
    except TypeError:
        # GET request without ?page=int
        page_number = 1
    
    page_obj = paginator.get_page(page_number)
    return render(request, "peaks/index.html", {
        "page_obj": page_obj,
        "title": title})


def region(request, slug):
    if Region.objects.filter(slug=slug).exists():
        region = Region.objects.get(slug=slug)
        allpeaks = Peak.objects.filter(region=region).order_by("-ele")   
        title = f"Peaks of {region.name}"
    elif Country.objects.filter(slug=slug).exists():
        country = Country.objects.get(slug=slug)
        allpeaks = Peak.objects.filter(countries=country).order_by("-ele") 
        title = f"Peaks of {country.name}"

    paginator = Paginator(allpeaks, PEAKSPERPAGE)
    
    try:
        page_number = int(request.GET.get('page'))
    except TypeError:
        # GET request without ?page=int
        page_number = 1
    
    page_obj = paginator.get_page(page_number)
    return render(request, "peaks/index.html", {
        "page_obj": page_obj,
        "title": title})

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