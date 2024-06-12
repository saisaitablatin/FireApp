from django.contrib import admin
from django.urls import path

from fire.views import (
    HomePageView,
    ChartView,
    PieCountbySeverity,
    LineCountbyMonth,
    MultilineIncidentTop3Country,
    MultipleBarbySeverity,
    MapStation,
    BarFirefighterExperience,
    PieFireTruckCapacity,
    LineIncidentSeverityOverTime,
    HistogramTemperatureDuringIncidents,
    HorizontalBarIncidentsByCity,
    FireIncidentsMap,
    get_incidents_by_location,
    LocationListView,
    LocationCreateView,
    LocationUpdateView,
    LocationDeleteView,
    IncidentListView,
    IncidentCreateView,
    IncidentUpdateView,
    IncidentDeleteView,
    FireStationListView,
    FireStationCreateView,
    FireStationUpdateView,
    FireStationDeleteView,
    FirefighterListView,
    FirefighterCreateView,
    FirefighterUpdateView,
    FirefighterDeleteView,
    FireTruckListView,
    FireTruckCreateView,
    FireTruckUpdateView,
    FireTruckDeleteView,
    WeatherConditionListView,
    WeatherConditionCreateView,
    WeatherConditionUpdateView,
    WeatherConditionDeleteView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", HomePageView.as_view(), name="home"),
    path("dashboard_chart/", ChartView.as_view(), name="dashboard-chart"),
    path("chart/", PieCountbySeverity, name="chart"),
    path("lineChart/", LineCountbyMonth, name="chart"),
    path("multilineChart/", MultilineIncidentTop3Country, name="chart"),
    path("multiBarChart/", MultipleBarbySeverity, name="chart"),
    path("stations/", MapStation, name="map-station"),
    path("fire_incidents/", FireIncidentsMap, name="fire-incidents-map"),
    path(
        "api/incidents_by_location/<str:location>/",
        get_incidents_by_location,
        name="get-incidents-by-location",
    ),
    path(
        "barFirefighterExperience/",
        BarFirefighterExperience,
        name="bar-firefighter-experience",
    ),
    path("pieFireTruckCapacity/", PieFireTruckCapacity, name="pie-fire-truck-capacity"),
    path(
        "lineIncidentSeverityOverTime/",
        LineIncidentSeverityOverTime,
        name="line-incident-severity-over-time",
    ),
    path(
        "histogramTemperatureDuringIncidents/",
        HistogramTemperatureDuringIncidents,
        name="histogram-temperature-during-incidents",
    ),
    path(
        "horizontalBarIncidentsByCity/",
        HorizontalBarIncidentsByCity,
        name="horizontal-bar-incidents-by-city",
    ),
    path("locations/", LocationListView.as_view(), name="location-list"),
    path("locations/new/", LocationCreateView.as_view(), name="location-create"),
    path(
        "locations/<int:pk>/edit/", LocationUpdateView.as_view(), name="location-update"
    ),
    path(
        "locations/<int:pk>/delete/",
        LocationDeleteView.as_view(),
        name="location-delete",
    ),
    path("incidents/", IncidentListView.as_view(), name="incident-list"),
    path("incidents/new/", IncidentCreateView.as_view(), name="incident-create"),
    path(
        "incidents/<int:pk>/edit/", IncidentUpdateView.as_view(), name="incident-update"
    ),
    path(
        "incidents/<int:pk>/delete/",
        IncidentDeleteView.as_view(),
        name="incident-delete",
    ),
    path("firestations/", FireStationListView.as_view(), name="firestation-list"),
    path(
        "firestations/new/", FireStationCreateView.as_view(), name="firestation-create"
    ),
    path(
        "firestations/<int:pk>/edit/",
        FireStationUpdateView.as_view(),
        name="firestation-update",
    ),
    path(
        "firestations/<int:pk>/delete/",
        FireStationDeleteView.as_view(),
        name="firestation-delete",
    ),
    path("firefighters/", FirefighterListView.as_view(), name="firefighter-list"),
    path(
        "firefighters/new/", FirefighterCreateView.as_view(), name="firefighter-create"
    ),
    path(
        "firefighters/<int:pk>/edit/",
        FirefighterUpdateView.as_view(),
        name="firefighter-update",
    ),
    path(
        "firefighters/<int:pk>/delete/",
        FirefighterDeleteView.as_view(),
        name="firefighter-delete",
    ),
    path("firetrucks/", FireTruckListView.as_view(), name="firetruck-list"),
    path("firetrucks/new/", FireTruckCreateView.as_view(), name="firetruck-create"),
    path(
        "firetrucks/<int:pk>/edit/",
        FireTruckUpdateView.as_view(),
        name="firetruck-update",
    ),
    path(
        "firetrucks/<int:pk>/delete/",
        FireTruckDeleteView.as_view(),
        name="firetruck-delete",
    ),
    path(
        "weatherconditions/",
        WeatherConditionListView.as_view(),
        name="weathercondition-list",
    ),
    path(
        "weatherconditions/new/",
        WeatherConditionCreateView.as_view(),
        name="weathercondition-create",
    ),
    path(
        "weatherconditions/<int:pk>/edit/",
        WeatherConditionUpdateView.as_view(),
        name="weathercondition-update",
    ),
    path(
        "weatherconditions/<int:pk>/delete/",
        WeatherConditionDeleteView.as_view(),
        name="weathercondition-delete",
    ),
]
