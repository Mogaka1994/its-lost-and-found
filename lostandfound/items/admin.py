from django.contrib import admin
from arcutils import admin as arc_admin

from .models import Location
from .models import Category


class CategoryAdmin(admin.ModelAdmin):
    exclude = ('machine_name',)

arc_admin.cas_site.register(Location)
arc_admin.cas_site.register(Category, CategoryAdmin)
