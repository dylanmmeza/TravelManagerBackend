from django.urls import path

from . import views

urlpatterns = [
    path("create_trip_tag/", views.create_trip_tag, name="create_trip_tag"),
    path(
        "create_trip_tag_usage/",
        views.create_trip_tag_usage,
        name="create_trip_tag_usage",
    ),
    path(
        "update_trip_tag_usage/",
        views.update_trip_tag_usage,
        name="update_trip_tag_usage",
    ),
    path("create_event_tag/", views.create_event_tag, name="create_event_tag"),
    path(
        "create_event_tag_usage/",
        views.create_event_tag_usage,
        name="create_event_tag_usage",
    ),
    path(
        "update_event_tag_usage/",
        views.update_event_tag_usage,
        name="update_event_tag_usage",
    ),
    path(
        "delete_trip_tag_usage/",
        views.delete_trip_tag_usage,
        name="delete_trip_tag_usage",
    ),
    path(
        "delete_event_tag_usage/",
        views.delete_event_tag_usage,
        name="delete_event_tag_usage",
    ),
    path("get_trip_tag_usages/", views.get_trip_tag_usages, name="get_trip_tag_usages"),
    path(
        "get_event_tag_usages/", views.get_event_tag_usages, name="get_event_tag_usages"
    ),
]
