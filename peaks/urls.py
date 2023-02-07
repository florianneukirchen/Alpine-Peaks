from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("peak/<int:id>", views.peak, name="peak"),
]