from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("peak/<slug:slug>", views.peak, name="peak"),
    path("region/<slug:slug>", views.index, name="region"),
    path("json/<slug:slug>", views.jsonapi, name="jsonapi"),
    path("json/", views.jsonapi, name="jsonapi"),
    path("region/", views.regionlist, name="regionlist"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("profile/<str:username>", views.profile, name="profile"),
    path("tour/<int:id>", views.showtour, name="showtour"),
    path("tour/", views.showtour, name="tourlist"),
    path("edit/<int:id>", views.tour, name="edittour"),
    path("edit/", views.tour, name="newtour"),
    path("waypoints/<int:id>", views.waypoints, name="waypoints"),
    path("likes/<int:id>", views.likes, name="likes"),
]