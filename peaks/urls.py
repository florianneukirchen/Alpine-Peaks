from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("peak/<slug:slug>", views.peak, name="peak"),
    path("region/<slug:slug>", views.region, name="region"),
    path("region/", views.regionlist, name="regionlist"),
]