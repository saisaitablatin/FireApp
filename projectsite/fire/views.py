from django.shortcuts import render
from django.views.generic.list import ListView
from django.db import connection
from django.http import JsonResponse
from django.db.models.functions import ExtractMonth
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from django.db.models import Count, Avg, F
from datetime import datetime
from fire.models import (
    Firefighters,
    FireTruck,
    Incident,
    WeatherConditions,
    Locations,
    FireStation,
)


class HomePageView(ListView):
    model = Locations
    context_object_name = "home"
    template_name = "home.html"


class ChartView(ListView):
    template_name = "chart.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_queryset(self, *args, **kwargs):
        pass


def PieCountbySeverity(request):
    query = """
    SELECT severity_level, COUNT(*) as count
    FROM fire_incident
    GROUP BY severity_level
    """
    data = {}
    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()

    if rows:
        # Construct the dictionary with severity level as keys and count as values
        data = {severity: count for severity, count in rows}
    else:
        data = {}

    return JsonResponse(data)


def LineCountbyMonth(request):

    current_year = datetime.now().year

    result = {month: 0 for month in range(1, 13)}

    incidents_per_month = Incident.objects.filter(
        date_time__year=current_year
    ).values_list("date_time", flat=True)

    # Counting the number of incidents per month
    for date_time in incidents_per_month:
        month = date_time.month
        result[month] += 1

    # If you want to convert month numbers to month names, you can use a dictionary mapping
    month_names = {
        1: "Jan",
        2: "Feb",
        3: "Mar",
        4: "Apr",
        5: "May",
        6: "Jun",
        7: "Jul",
        8: "Aug",
        9: "Sep",
        10: "Oct",
        11: "Nov",
        12: "Dec",
    }

    result_with_month_names = {
        month_names[int(month)]: count for month, count in result.items()
    }

    return JsonResponse(result_with_month_names)


def MultilineIncidentTop3Country(request):

    query = """
        SELECT 
        fl.country,
        strftime('%m', fi.date_time) AS month,
        COUNT(fi.id) AS incident_count
    FROM 
        fire_incident fi
    JOIN 
        fire_locations fl ON fi.location_id = fl.id
    WHERE 
        fl.country IN (
            SELECT 
                fl_top.country
            FROM 
                fire_incident fi_top
            JOIN 
                fire_locations fl_top ON fi_top.location_id = fl_top.id
            WHERE 
                strftime('%Y', fi_top.date_time) = strftime('%Y', 'now')
            GROUP BY 
                fl_top.country
            ORDER BY 
                COUNT(fi_top.id) DESC
            LIMIT 3
        )
        AND strftime('%Y', fi.date_time) = strftime('%Y', 'now')
    GROUP BY 
        fl.country, month
    ORDER BY 
        fl.country, month;
    """

    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()

    # Initialize a dictionary to store the result
    result = {}

    # Initialize a set of months from January to December
    months = set(str(i).zfill(2) for i in range(1, 13))

    # Loop through the query results
    for row in rows:
        country = row[0]
        month = row[1]
        total_incidents = row[2]

        # If the country is not in the result dictionary, initialize it with all months set to zero
        if country not in result:
            result[country] = {month: 0 for month in months}

        # Update the incident count for the corresponding month
        result[country][month] = total_incidents

    # Ensure there are always 3 countries in the result
    while len(result) < 3:
        # Placeholder name for missing countries
        missing_country = f"Country {len(result) + 1}"
        result[missing_country] = {month: 0 for month in months}

    for country in result:
        result[country] = dict(sorted(result[country].items()))

    return JsonResponse(result)


def MultipleBarbySeverity(request):
    query = """
    SELECT 
        fi.severity_level,
        strftime('%m', fi.date_time) AS month,
        COUNT(fi.id) AS incident_count
    FROM 
        fire_incident fi
    GROUP BY fi.severity_level, month
    """

    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()

    result = {}
    months = set(str(i).zfill(2) for i in range(1, 13))

    for row in rows:
        level = str(row[0])  # Ensure the severity level is a string
        month = row[1]
        total_incidents = row[2]

        if level not in result:
            result[level] = {month: 0 for month in months}

        result[level][month] = total_incidents

    # Sort months within each severity level
    for level in result:
        result[level] = dict(sorted(result[level].items()))

    return JsonResponse(result)


def MapStation(request):
    fireStations = FireStation.objects.values("name", "latitude", "longitude")

    for fs in fireStations:
        fs["latitude"] = float(fs["latitude"])
        fs["longitude"] = float(fs["longitude"])

    fireStations_list = list(fireStations)

    context = {
        "fireStations": fireStations_list,
    }

    return render(request, "map_station.html", context)


def FireIncidentsMap(request):
    incidents = Incident.objects.values(
        "location__name", "location__latitude", "location__longitude", "severity_level"
    )

    for incident in incidents:
        incident["location__latitude"] = float(incident["location__latitude"])
        incident["location__longitude"] = float(incident["location__longitude"])

    incidents_list = list(incidents)

    context = {
        "incidents": incidents_list,
    }

    return render(request, "fire_incidents.html", context)


def get_incidents_by_location(request, location):
    incidents = Incident.objects.filter(location__name=location).values(
        "location__latitude", "location__longitude", "severity_level", "location__name"
    )

    for incident in incidents:
        incident["location__latitude"] = float(incident["location__latitude"])
        incident["location__longitude"] = float(incident["location__longitude"])

    incidents_list = list(incidents)
    return JsonResponse(incidents_list, safe=False)


def BarFirefighterExperience(request):
    data = Firefighters.objects.values("experience_level").annotate(count=Count("id"))
    result = {entry["experience_level"]: entry["count"] for entry in data}
    return JsonResponse(result)


def PieFireTruckCapacity(request):
    data = FireTruck.objects.values("capacity").annotate(count=Count("id"))
    result = {entry["capacity"]: entry["count"] for entry in data}
    return JsonResponse(result)


def LineIncidentSeverityOverTime(request):
    data = (
        Incident.objects.extra(select={"month": "strftime('%Y-%m', date_time)"})
        .values("month", "severity_level")
        .annotate(count=Count("id"))
        .order_by("month")
    )
    result = {}
    for entry in data:
        month = entry["month"]
        if month not in result:
            result[month] = {"Minor Fire": 0, "Moderate Fire": 0, "Major Fire": 0}
        result[month][entry["severity_level"]] = entry["count"]
    return JsonResponse(result)


def HistogramTemperatureDuringIncidents(request):
    data = (
        WeatherConditions.objects.values("temperature")
        .annotate(count=Count("id"))
        .order_by("temperature")
    )
    result = {float(entry["temperature"]): entry["count"] for entry in data}
    return JsonResponse(result)


def HorizontalBarIncidentsByCity(request):
    data = (
        Incident.objects.values(city=F("location__city"))
        .annotate(count=Count("id"))
        .order_by("-count")
    )
    result = {entry["city"]: entry["count"] for entry in data}
    return JsonResponse(result)


# Location Views
class LocationListView(ListView):
    model = Locations
    template_name = "location_list.html"


class LocationCreateView(CreateView):
    model = Locations
    fields = "__all__"
    template_name = "location_form.html"
    success_url = reverse_lazy("location-list")


class LocationUpdateView(UpdateView):
    model = Locations
    fields = "__all__"
    template_name = "location_form.html"
    success_url = reverse_lazy("location-list")


class LocationDeleteView(DeleteView):
    model = Locations
    template_name = "location_confirm_delete.html"
    success_url = reverse_lazy("location-list")


# Incident Views
class IncidentListView(ListView):
    model = Incident
    template_name = "incident_list.html"


class IncidentCreateView(CreateView):
    model = Incident
    fields = "__all__"
    template_name = "incident_form.html"
    success_url = reverse_lazy("incident-list")


class IncidentUpdateView(UpdateView):
    model = Incident
    fields = "__all__"
    template_name = "incident_form.html"
    success_url = reverse_lazy("incident-list")


class IncidentDeleteView(DeleteView):
    model = Incident
    template_name = "incident_confirm_delete.html"
    success_url = reverse_lazy("incident-list")


# FireStation Views
class FireStationListView(ListView):
    model = FireStation
    template_name = "firestation_list.html"


class FireStationCreateView(CreateView):
    model = FireStation
    fields = "__all__"
    template_name = "firestation_form.html"
    success_url = reverse_lazy("firestation-list")


class FireStationUpdateView(UpdateView):
    model = FireStation
    fields = "__all__"
    template_name = "firestation_form.html"
    success_url = reverse_lazy("firestation-list")


class FireStationDeleteView(DeleteView):
    model = FireStation
    template_name = "firestation_confirm_delete.html"
    success_url = reverse_lazy("firestation-list")


# Firefighter Views
class FirefighterListView(ListView):
    model = Firefighters
    template_name = "firefighter_list.html"


class FirefighterCreateView(CreateView):
    model = Firefighters
    fields = "__all__"
    template_name = "firefighter_form.html"
    success_url = reverse_lazy("firefighter-list")


class FirefighterUpdateView(UpdateView):
    model = Firefighters
    fields = "__all__"
    template_name = "firefighter_form.html"
    success_url = reverse_lazy("firefighter-list")


class FirefighterDeleteView(DeleteView):
    model = Firefighters
    template_name = "firefighter_confirm_delete.html"
    success_url = reverse_lazy("firefighter-list")


# FireTruck Views
class FireTruckListView(ListView):
    model = FireTruck
    template_name = "firetruck_list.html"


class FireTruckCreateView(CreateView):
    model = FireTruck
    fields = "__all__"
    template_name = "firetruck_form.html"
    success_url = reverse_lazy("firetruck-list")


class FireTruckUpdateView(UpdateView):
    model = FireTruck
    fields = "__all__"
    template_name = "firetruck_form.html"
    success_url = reverse_lazy("firetruck-list")


class FireTruckDeleteView(DeleteView):
    model = FireTruck
    template_name = "firetruck_confirm_delete.html"
    success_url = reverse_lazy("firetruck-list")


# WeatherCondition Views
class WeatherConditionListView(ListView):
    model = WeatherConditions
    template_name = "weathercondition_list.html"


class WeatherConditionCreateView(CreateView):
    model = WeatherConditions
    fields = "__all__"
    template_name = "weathercondition_form.html"
    success_url = reverse_lazy("weathercondition-list")


class WeatherConditionUpdateView(UpdateView):
    model = WeatherConditions
    fields = "__all__"
    template_name = "weathercondition_form.html"
    success_url = reverse_lazy("weathercondition-list")


class WeatherConditionDeleteView(DeleteView):
    model = WeatherConditions
    template_name = "weathercondition_confirm_delete.html"
    success_url = reverse_lazy("weathercondition-list")
