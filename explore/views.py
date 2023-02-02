import json
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from trips.models import Base_Trip


# Create your views here.
@login_required
def like_trip(request):
    data = json.loads(request.body)
    user_extension = request.user.profile
    trip_uuid = data["trip_uuid"]
    trip = Base_Trip.active.prefetch_related("users_that_liked_trip").get(
        _trip_uuid=trip_uuid
    )
    if user_extension not in trip.users_that_liked_trip.all():
        trip.users_that_liked_trip.add(user_extension)
        return JsonResponse({"valid": True, "message": "Liked trip"})


@login_required
def unlike_trip(request):
    data = json.loads(request.body)
    user_extension = request.user.profile
    trip_uuid = data["trip_uuid"]
    trip = Base_Trip.active.prefetch_related("users_that_liked_trip").get(
        _trip_uuid=trip_uuid
    )
    if user_extension in trip.users_that_liked_trip.all():
        trip.users_that_liked_trip.remove(user_extension)
        return JsonResponse({"valid": True, "message": "Unlike trip"})


@login_required
def star_trip(request):
    data = json.loads(request.body)
    user_extension = request.user.profile
    trip_uuid = data["trip_uuid"]
    trip = Base_Trip.active.prefetch_related("users_that_starred_trip").get(
        _trip_uuid=trip_uuid
    )
    if user_extension not in trip.users_that_starred_trip.all():
        trip.users_that_starred_trip.add(user_extension)
        return JsonResponse({"valid": True, "message": "Star trip"})


@login_required
def unstar_trip(request):
    data = json.loads(request.body)
    user_extension = request.user.profile
    trip_uuid = data["trip_uuid"]
    trip = Base_Trip.active.prefetch_related("users_that_starred_trip").get(
        _trip_uuid=trip_uuid
    )
    if user_extension in trip.users_that_starred_trip.all():
        trip.users_that_starred_trip.remove(user_extension)
        return JsonResponse({"valid": True, "message": "Unstarred trip"})


@login_required
def question_trip(request):
    data = json.loads(request.body)
    user_extension = request.user.profile
    trip_uuid = data["trip_uuid"]
    trip = Base_Trip.active.prefetch_related("users_that_questioned_trip").get(
        _trip_uuid=trip_uuid
    )
    if user_extension not in trip.users_that_questioned_trip.all():
        trip.users_that_questioned_trip.add(user_extension)
        return JsonResponse({"valid": True, "message": "Questioned trip"})


@login_required
def unquestion_trip(request):
    data = json.loads(request.body)
    user_extension = request.user.profile
    trip_uuid = data["trip_uuid"]
    trip = Base_Trip.active.prefetch_related("users_that_questioned_trip").get(
        _trip_uuid=trip_uuid
    )
    if user_extension in trip.users_that_questioned_trip.all():
        trip.users_that_questioned_trip.remove(user_extension)
        return JsonResponse({"valid": True, "message": "Unquestioned trip"})


@login_required
def get_friend_trips(request):
    trip_data = []
    user_extension = request.user.profile
    my_friends = user_extension.my_friends.all()
    for friend in my_friends:
        friend_trips = Base_Trip.active.filter(trip_owner=friend)
        for trip in friend_trips:
            trip_data.append(trip.summary())
    return JsonResponse({"valid": True, "message": "FYP Trips", "response": trip_data})


@login_required
def get_fyp_trips(request):
    trip_data = []
    trips = Base_Trip.active.filter(public=True)
    for trip in trips:
        trip_data.append(trip.trip_details())
    return JsonResponse({"valid": True, "message": "FYP Trips", "response": trip_data})
