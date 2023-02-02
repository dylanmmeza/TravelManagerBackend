from django.urls import path

from . import views

urlpatterns = [
    path(
        "create_unplanned_trip/",
        views.create_unplanned_trip,
        name="create_unplanned_trip",
    ),
    path("create_planned_trip/", views.create_planned_trip, name="create_planned_trip"),
    path("update_trip/", views.update_trip, name="update_trip"),
    path("delete_trip/", views.delete_trip, name="delete_trip"),
    path("create_destination/", views.create_destination, name="create_destination"),
    path("add_destination/", views.add_destination, name="add_destination"),
    path("remove_destination/", views.remove_destination, name="remove_destination"),
    path("get_trips/", views.get_trips, name="get_trips"),
    path("my_trips/", views.my_trips, name="my_trips"),
    path("trip_details/", views.trip_details, name="trip_details"),
    path("add_authorized_user/", views.add_authorized_user, name="add_authorized_user"),
    path(
        "remove_authorized_user/",
        views.remove_authorized_user,
        name="remove_authorized_user",
    ),
    path("joined_trips/", views.joined_trips, name="joined_trips"),
    path("pending_trips/", views.pending_trips, name="pending_trips"),
    path("get_liked_trips/", views.get_liked_trips, name="get_liked_trips"),
    path("get_starred_trips/", views.get_starred_trips, name="get_starred_trips"),
    path(
        "get_questioned_trips/",
        views.get_questioned_trips,
        name="get_questioned_trips",
    ),
    path("get_destinations/", views.get_destinations, name="get_destinations"),
    path(
        "create_default_destinations/",
        views.create_default_destinations,
        name="create_default_destinations",
    ),
]
