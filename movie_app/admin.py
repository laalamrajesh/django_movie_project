from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(Actor)
admin.site.register(Movie)
admin.site.register(MovieCast)
admin.site.register(MovieRating)

admin.site.register(Rating)