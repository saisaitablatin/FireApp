import random
import json
from django.shortcuts import render
from django.views.generic.list import ListView
from django.db import connection
from django.http import JsonResponse
from django.db.models.functions import ExtractMonth


from django.db.models import Count
from datetime import datetime
from FireApp.models import FireIncident, FireLocation, FireStation


# Create your views here.


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
    FROM FireApp_fireincident
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

    incidents_per_month = FireIncident.objects.filter(
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
        FireApp_fireincident fi
    JOIN 
        FireApp_firelocation fl ON fi.location_id = fl.id
    WHERE 
        fl.country IN (
            SELECT 
                fl_top.country
            FROM 
                FireApp_fireincident fi_top
            JOIN 
                FireApp_firelocation fl_top ON fi_top.location_id = fl_top.id
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


def multipleBarbySeverity(request):
    query = """
    SELECT 
        fi.severity_level,
        strftime('%m', fi.date_time) AS month,
        COUNT(fi.id) AS incident_count
    FROM 
        FireApp_fireincident fi
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


# Predefined coordinates for barangays in Puerto Princesa City
barangay_coordinates = {
    "Barangay San Pedro": (9.759001431851921, 118.75786335104155),
    "Barangay Mandaragat": (9.748646551957371, 118.73964419467723),
    "Barangay San Miguel": (9.74757389879427, 118.75642401298171),
    "Barangay San Jose": (9.794098800097737, 118.75921266844219),
    "Barangay Tiniguiban": (9.771414551960454, 118.74452901673914),
    "Barangay San Manuel": (9.771700446692131, 118.76425827599432),
    "Barangay Santa Monica": (9.788931598544831, 118.73093532877895),
    "Barangay Tagburos": (9.822344379670465, 118.74394796348989),
    "Barangay Manggahan": (9.73990456054043, 118.73908841261942),
}


def map_station(request):
    city = request.GET.get("city", None)

    fireStations = FireStation.objects.all()
    fireIncidents = FireIncident.objects.all()

    if city:
        fireStations = fireStations.filter(location__country=city)
        fireIncidents = fireIncidents.filter(location__country=city)

    fireStations_list = list(fireStations.values("name", "latitude", "longitude"))
    for station in fireStations_list:
        station["latitude"] = float(station["latitude"])
        station["longitude"] = float(station["longitude"])

    fireIncidents_list = []
    for incident in fireIncidents:
        if incident.latitude is None or incident.longitude is None:
            barangay_name = incident.location.country.split(",")[
                0
            ].strip()  # Assuming location country stores barangay name
            if barangay_name in barangay_coordinates:
                incident.latitude = random.uniform(
                    barangay_coordinates[barangay_name][0] - 0.008,
                    barangay_coordinates[barangay_name][0] + 0.008,
                )
                incident.longitude = random.uniform(
                    barangay_coordinates[barangay_name][1] - 0.008,
                    barangay_coordinates[barangay_name][1] + 0.008,
                )
            else:
                # Generate random coordinates within the initial map view bounds as a fallback
                incident.latitude = random.uniform(9.805, 9.828)
                incident.longitude = random.uniform(118.710, 118.740)
            incident.save()

        fireIncidents_list.append(
            {
                "date_time": incident.date_time.isoformat(),
                "severity_level": incident.severity_level,
                "latitude": float(incident.latitude),
                "longitude": float(incident.longitude),
                "location_country": incident.location.country,
            }
        )

    cities = FireLocation.objects.values_list("country", flat=True).distinct()

    context = {
        "fireStations": fireStations_list,
        "fireIncidents": json.dumps(fireIncidents_list),
        "cities": cities,
        "selected_city": city,
    }

    return render(request, "mapstation.html", context)
