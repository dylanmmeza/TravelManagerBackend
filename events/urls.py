from django.urls import path

from . import views

urlpatterns = [
    path(
        "create_planned_event/", views.create_planned_event, name="create_planned_event"
    ),
    path(
        "create_unplanned_event/",
        views.create_unplanned_event,
        name="create_unplanned_event",
    ),
    path("create_air_travel/", views.create_air_travel, name="create_air_travel"),
    path("create_car_travel/", views.create_car_travel, name="create_car_travel"),
    path("create_lodging/", views.create_lodging, name="create_lodging"),
    path("create_location/", views.create_location, name="create_location"),
    path("delete_event/", views.delete_event, name="delete_event"),
    path("reactivate_event/", views.reactivate_event, name="reactivate_event"),
    path(
        "update_generic_event/", views.update_generic_event, name="update_generic_event"
    ),
    path("update_air_travel/", views.update_air_travel, name="update_air_travel"),
    path("update_car_travel/", views.update_car_travel, name="update_car_travel"),
    path("update_lodging/", views.update_lodging, name="update_lodging"),
    path("google_places_api/", views.google_places_api, name="google_places_api"),
    path("airline_api/", views.airline_api, name="airline_api"),
    path("get_all_events/", views.get_all_events, name="get_all_events"),
]
