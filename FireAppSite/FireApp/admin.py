from django.contrib import admin
from FireApp.models import FireStation, FireLocation, FireIncident


# Register your models here.
@admin.register(FireStation)
class FireStationAdmin(admin.ModelAdmin):
    list_display = ("name", "latitude", "longitude", "address", "location")


admin.site.register(FireIncident)
admin.site.register(FireLocation)
