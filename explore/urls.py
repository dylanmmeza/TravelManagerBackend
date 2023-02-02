from django.urls import path

from . import views

urlpatterns = [
    path("like_trip/", views.like_trip, name="like_trip"),
    path("unlike_trip/", views.unlike_trip, name="unlike_trip"),
    path("star_trip/", views.star_trip, name="star_trip"),
    path("unstar_trip/", views.unstar_trip, name="unstar_trip"),
    path("question_trip/", views.question_trip, name="question_trip"),
    path("unquestion_trip/", views.unquestion_trip, name="unquestion_trip"),
    path("get_friend_trips/", views.get_friend_trips, name="get_friend_trips"),
    path("get_fyp_trips/", views.get_fyp_trips, name="get_fyp_trips"),
]
