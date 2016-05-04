from django.contrib import admin

from .items.models import Location


site = admin.site
site.register(Location)
