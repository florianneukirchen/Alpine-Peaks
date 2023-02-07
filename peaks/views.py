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
    allpeaks = Peak.objects.all().order_by("-neargtdist")
    paginator = Paginator(allpeaks, PEAKSPERPAGE)
    try:
        page_number = int(request.GET.get('page'))
    except TypeError:
        # GET request without ?page=int
        page_number = 1
    page_obj = paginator.get_page(page_number)
    return render(request, "peaks/index.html", {
        "page_obj": page_obj,
        "title": "Peaks of the Alps"})


def peak(request, id):
    try:
        peak = Peak.objects.get(id=id)
    except Peak.DoesNotExist:
        raise Http404("Page not found")

    return render(request, "peaks/peak.html", {
        "peak": peak,
    })