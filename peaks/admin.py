from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(User)
admin.site.register(Peak)
admin.site.register(Tour)
admin.site.register(Region)
admin.site.register(Waypoint)
# admin.site.register(Country)