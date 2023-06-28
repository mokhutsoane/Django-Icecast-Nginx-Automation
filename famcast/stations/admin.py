from django.contrib import admin

from .models import Station

@admin.register(Station)
class StationAdmin(admin.ModelAdmin):
    list_display = ('name', 'port', 'limit', 'mount', 'hostname', 'station_key')
