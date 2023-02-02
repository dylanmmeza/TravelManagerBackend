from django.http import JsonResponse

import json
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.utils.dateparse import parse_datetime, parse_duration
from django.db.models import Q

from tags.models import TripTag
from events.models import Base_event
from users.models import User_extension

from trips.models import (
    Base_Trip,
    Destination,
    Planned_trip,
    Unplanned_trip,
)
from tags.models import TripTagUsage, TripTag


# Create your views here.
@login_required
@transaction.atomic
def create_unplanned_trip(request):
    data = json.loads(request.body)
    user_extension = request.user.profile
    unplanned_trip = Unplanned_trip()
    setattr(unplanned_trip, "trip_owner", user_extension)
    unplanned_trip.populate_values(data)
    unplanned_trip.save()

    return JsonResponse(
        {
            "valid": True,
            "message": "Trip Created",
            "trip": unplanned_trip.summary(),
        }
    )


@login_required
@transaction.atomic
def create_planned_trip(request):
    data = json.loads(request.body)

    if "start_time" not in data or "end_time" not in data:
        return JsonResponse({"valid": False, "message": "Missing Trip Dates"})

    user_extension = request.user.profile
    start_time = parse_datetime(data["start_time"])
    end_time = parse_datetime(data["end_time"])

    planned_trip = Planned_trip(start_time=start_time, end_time=end_time)
    setattr(planned_trip, "trip_owner", user_extension)
    planned_trip.populate_values(data)
    planned_trip.save()

    if "tags" in data:
        tags = data["tags"]
        for t in tags:
            tag_object = TripTag()
            tag_object.populate_values(t, user_extension)
            TripTagUsage.objects.create(trip=planned_trip, trip_tag=tag_object)
    planned_trip.save()

    return JsonResponse(
        {
            "valid": True,
            "message": "Trip Created",
            "trip": planned_trip.summary(),
        }
    )


@login_required
@transaction.atomic
def delete_trip(request):
    data = json.loads(request.body)
    user_extension = request.user.profile
    _trip_uuid = data["trip_uuid"]
    trip = Base_Trip.active.get(_trip_uuid=_trip_uuid)
    if trip.trip_owner == user_extension:
        setattr(trip, "is_deleted", True)
        trip.save()
        return JsonResponse(
            {
                "valid": True,
                "message": "Trip Deleted",
                "trip": trip.trip_summary(),
            }
        )
    else:
        return JsonResponse(
            {
                "valid": False,
                "message": "Not the trip Owner",
                "trip": trip.trip_summary(),
            }
        )


@login_required
@transaction.atomic
def update_trip(request):
    data = json.loads(request.body)
    user_extension = request.user.profile
    trip_uuid = data["trip_uuid"]
    trips = (
        Base_Trip.active.select_related("unplanned_trip")
        .select_related("planned_trip")
        .get(_trip_uuid=trip_uuid)
    )
    if hasattr(trips, "planned_trip"):
        trip = Planned_trip.active.get(_trip_uuid=trip_uuid)

    elif hasattr(trips, "unplanned_trip"):
        trip = Unplanned_trip.active.get(_trip_uuid=trip_uuid)
    LIST_OF_ATTRIBUTES = [
        "start_time",
        "end_time",
        "trip_name",
        "num_people",
        "public",
        "trip_img",
        "alert_time",
        "trip_icon",
        "trip_icon_color",
        "trip_description",
    ]
    if trip.trip_owner == user_extension:
        for atr in LIST_OF_ATTRIBUTES:
            if atr in data:
                if atr == "start_time" or atr == "end_time":
                    parsed_value = parse_datetime(data[atr])
                    setattr(trip, atr, parsed_value)
                elif atr == "alert_time":
                    parsed_value = parse_duration(data[atr])
                else:
                    setattr(trip, atr, data[atr])
        trip.save()
        return JsonResponse(
            {
                "valid": True,
                "message": "Trip Updated",
                "details": trip.details(),
            }
        )
    else:
        return JsonResponse(
            {
                "valid": False,
                "message": "Not Trip Owner",
                "trip": trip.details(),
            }
        )


@login_required
@transaction.atomic
def create_destination(request):
    data = json.loads(request.body)
    destination_name = data["destination_name"]
    user_extension = request.user.profile
    destination = Destination.create_destination(destination_name, user_extension)
    return JsonResponse(
        {
            "valid": True,
            "message": "Destination Created",
            "trip": destination.summary(),
        }
    )


@login_required
@transaction.atomic
def add_destination(request):
    data = json.loads(request.body)
    destination_uuid = data["destination_uuid"]
    destination = Destination.objects.get(_destination_uuid=destination_uuid)
    user_extension = request.user.profile
    trip_uuid = data["trip_uuid"]

    trip = (
        Base_Trip.active.select_related("trip_owner")
        .select_related("unplanned_trip")
        .select_related("planned_trip")
        .get(_trip_uuid=trip_uuid)
    )

    if hasattr(trip, "planned_trip"):
        trip = Planned_trip.active.get(_trip_uuid=trip_uuid)
    elif hasattr(trip, "unplanned_trip"):
        trip = Unplanned_trip.active.get(_trip_uuid=trip_uuid)

    destinations_by_uuid = trip.destinations.all().in_bulk(
        field_name="_destination_uuid"
    )

    authorized_users_by_uuid = trip.authorized_users.all().in_bulk(
        field_name="_user_uuid"
    )
    authorized_user = authorized_users_by_uuid.get(user_extension._user_uuid, None)

    if authorized_user or user_extension == trip.trip_owner:
        existing_destinations = destinations_by_uuid.get(
            destination._destination_uuid, None
        )
        if not existing_destinations:
            trip.destinations.add(destination)
            trip.save()
            return JsonResponse(
                {
                    "valid": True,
                    "message": "Destination added",
                    "details": trip.details(),
                }
            )
        return JsonResponse({"valid": False, "message": "existing destination"})

    return JsonResponse({"valid": False, "message": "not Authorized User"})


@login_required
@transaction.atomic
def remove_destination(request):
    data = json.loads(request.body)
    destination_uuid = data["destination_uuid"]
    destination = Destination.objects.get(_destination_uuid=destination_uuid)
    user_extension = request.user.profile
    trip_uuid = data["trip_uuid"]

    trip = (
        Base_Trip.active.select_related("trip_owner")
        .select_related("unplanned_trip")
        .select_related("planned_trip")
        .get(_trip_uuid=trip_uuid)
    )

    if hasattr(trip, "planned_trip"):
        trip = Planned_trip.active.get(_trip_uuid=trip_uuid)
    elif hasattr(trip, "unplanned_trip"):
        trip = Unplanned_trip.active.get(_trip_uuid=trip_uuid)

    destinations_by_uuid = trip.destinations.all().in_bulk(
        field_name="_destination_uuid"
    )

    authorized_users_by_uuid = trip.authorized_users.all().in_bulk(
        field_name="_user_uuid"
    )
    authorized_user = authorized_users_by_uuid.get(user_extension._user_uuid, None)

    if authorized_user or user_extension == trip.trip_owner:
        existing_destinations = destinations_by_uuid.get(
            destination._destination_uuid, None
        )
        if existing_destinations:
            trip.destinations.remove(destination)
            trip.save()
            return JsonResponse(
                {
                    "valid": True,
                    "message": "Destination removed",
                    "details": trip.details(),
                }
            )


@login_required
@transaction.atomic
def add_authorized_user(request):
    data = json.loads(request.body)
    user_extension = request.user.profile
    # invite_type = data["invite_type"]
    invitee_uuid = data["invitee_uuid"]
    invitee = User_extension.active.get(_user_uuid=invitee_uuid)
    trip_uuid = data["trip_uuid"]
    trip = Base_Trip.active.select_related("trip_owner").get(_trip_uuid=trip_uuid)

    authorized_users_by_uuid = trip.authorized_users.all().in_bulk(
        field_name="_user_uuid"
    )
    authorized_user = authorized_users_by_uuid.get(user_extension._user_uuid, None)

    if authorized_user or user_extension == trip.trip_owner:
        existing_invitee = authorized_users_by_uuid.get(invitee._user_uuid, None)
        if not existing_invitee:
            trip.authorized_users.add(invitee)
            return JsonResponse(
                {
                    "valid": True,
                    "Message": "User added",
                    "response": trip.trip_summary(),
                }
            )
        else:
            return JsonResponse({"valid": False, "Message": "User already added"})
    return JsonResponse({"valid": False, "Message": "Invalid Request"})


@login_required
@transaction.atomic
def remove_authorized_user(request):
    data = json.loads(request.body)
    user_extension = request.user.profile
    invitee_uuid = data["invitee_uuid"]
    invitee = User_extension.active.get(_user_uuid=invitee_uuid)
    trip_uuid = data["trip_uuid"]
    trip = Base_Trip.active.select_related("trip_owner").get(_trip_uuid=trip_uuid)

    authorized_users_by_uuid = trip.authorized_users.all().in_bulk(
        field_name="_user_uuid"
    )
    authorized_user = authorized_users_by_uuid.get(user_extension._user_uuid, None)

    if authorized_user or user_extension == trip.trip_owner:
        existing_invitee = authorized_users_by_uuid.get(invitee._user_uuid, None)
        if existing_invitee:
            trip.authorized_users.remove(invitee)
            return JsonResponse(
                {
                    "valid": True,
                    "Message": "User removed",
                    "response": trip.trip_summary(),
                }
            )
        else:
            return JsonResponse({"valid": False, "Message": "User already removed"})


@login_required
@transaction.atomic
def joined_trips(request):
    user_extension = request.user.profile
    data = []

    trips = (
        Base_Trip.active.select_related("unplanned_trip")
        .select_related("planned_trip")
        .prefetch_related("authorized_users")
        .all()
    )
    for t in trips:
        authorized_users_by_uuid = t.authorized_users.all().in_bulk(
            field_name="_user_uuid"
        )
        authorized_user = authorized_users_by_uuid.get(user_extension._user_uuid, None)

        if authorized_user:
            if hasattr(t, "unplanned_trip"):
                data.append(t.unplanned_trip.summary())
            elif hasattr(t, "planned_trip"):
                data.append(t.planned_trip.summary())

    return JsonResponse({"valid": True, "trips": data})


@login_required
@transaction.atomic
def pending_trips(request):
    user_extension = request.user.profile
    data = []
    trips = (
        Base_Trip.active.select_related("unplanned_trip")
        .select_related("planned_trip")
        .prefetch_related("pending_permission")
        .all()
    )

    for t in trips:
        pending_users_by_uuid = t.pending_permission.all().in_bulk(
            field_name="_user_uuid"
        )
        pending_users = pending_users_by_uuid.get(user_extension._user_uuid, None)

        if pending_users:
            if hasattr(t, "unplanned_trip"):
                data.append(t.unplanned_trip.summary())
            elif hasattr(t, "planned_trip"):
                data.append(t.planned_trip.summary())

    return JsonResponse({"valid": True, "trips": data})


@login_required
@transaction.atomic
def get_liked_trips(request):
    user_extension = request.user.profile
    data = []
    trips = (
        Base_Trip.active.select_related("unplanned_trip")
        .select_related("planned_trip")
        .prefetch_related("users_that_liked_trip")
        .all()
    )
    for t in trips:
        users_that_liked_trip = t.users_that_liked_trip.all().in_bulk(
            field_name="_user_uuid"
        )
        liked_user = users_that_liked_trip.get(user_extension._user_uuid, None)

        if liked_user:
            if hasattr(t, "unplanned_trip"):
                data.append({"unplanned": t.unplanned_trip.summary()})
            elif hasattr(t, "planned_trip"):
                data.append({"planned": t.planned_trip.summary()})

    return JsonResponse({"valid": True, "response": data})


@login_required
@transaction.atomic
def get_starred_trips(request):
    user_extension = request.user.profile
    data = []
    trips = (
        Base_Trip.active.select_related("unplanned_trip")
        .select_related("planned_trip")
        .prefetch_related("users_that_starred_trip")
        .all()
    )
    for t in trips:
        users_that_starred_trip = t.users_that_starred_trip.all().in_bulk(
            field_name="_user_uuid"
        )
        starred_user = users_that_starred_trip.get(user_extension._user_uuid, None)

        if starred_user:
            if hasattr(t, "unplanned_trip"):
                data.append({"unplanned": t.unplanned_trip.summary()})
            elif hasattr(t, "planned_trip"):
                data.append({"planned": t.planned_trip.summary()})

    return JsonResponse({"valid": True, "response": data})


@login_required
@transaction.atomic
def get_questioned_trips(request):
    user_extension = request.user.profile
    data = []
    trips = (
        Base_Trip.active.select_related("unplanned_trip")
        .select_related("planned_trip")
        .prefetch_related("users_that_questioned_trip")
        .all()
    )
    for t in trips:
        users_that_questioned_trip = t.users_that_questioned_trip.all().in_bulk(
            field_name="_user_uuid"
        )
        questioned_user = users_that_questioned_trip.get(
            user_extension._user_uuid, None
        )

        if questioned_user:
            if hasattr(t, "unplanned_trip"):
                data.append({"unplanned": t.unplanned_trip.summary()})
            elif hasattr(t, "planned_trip"):
                data.append({"planned": t.planned_trip.summary()})

    return JsonResponse({"valid": True, "response": data})


@login_required
@transaction.atomic
def my_trips(request):
    data = []
    user_extension = request.user.profile
    my_trips = Base_Trip.active.filter(trip_owner=user_extension)
    my_trips = (
        Base_Trip.active.select_related("unplanned_trip")
        .select_related("planned_trip")
        .filter(trip_owner=user_extension)
    )

    for t in my_trips:
        if hasattr(t, "unplanned_trip"):
            data.append(t.unplanned_trip.summary())
        elif hasattr(t, "planned_trip"):
            data.append(t.planned_trip.summary())

    return JsonResponse({"valid": True, "trips": data})


@login_required
@transaction.atomic
def trip_details(request):
    data = json.loads(request.body)
    user_extension = request.user.profile
    details = {}

    trip_uuid = data["trip_uuid"]
    my_trip = (
        Base_Trip.active.select_related("unplanned_trip")
        .select_related("planned_trip")
        .prefetch_related("authorized_users")
        .get(_trip_uuid=trip_uuid)
    )
    authorized_users_by_uuid = my_trip.authorized_users.all().in_bulk(
        field_name="_user_uuid"
    )
    authorized_user = authorized_users_by_uuid.get(user_extension._user_uuid, None)

    if authorized_user or user_extension == my_trip.trip_owner:
        if hasattr(my_trip, "unplanned_trip"):
            details = my_trip.unplanned_trip.details()
        elif hasattr(my_trip, "planned_trip"):
            details = my_trip.planned_trip.details()

    return JsonResponse(
        {
            "valid": True,
            "details": details,
            "trip_uuid": trip_uuid,
            "message": "Details Returned",
        }
    )


# HELPERS


def get_trip(request):
    data = json.loads(request.body)
    trip_uuid = data["trip_uuid"]
    trip = (
        Base_Trip.active.select_related("unplanned_trip")
        .select_related("planned_trip")
        .get(_trip_uuid=trip_uuid)
    )
    trip_data = {}
    if hasattr(trip, "unplanned_trip"):
        data["summary"] = trip.unplanned_trip.trip_details()
    elif hasattr(trip, "planned_trip"):
        data["summary"] = trip.planned_trip.trip_details()

    trip_data["summary"] = trip.trip_details()
    trip_data["tags"] = [tag.summary() for tag in TripTag.objects.filter(trip=trip)]
    trip_data["events"] = [
        event.summary() for event in Base_event.objects.filter(trip=trip)
    ]
    return JsonResponse({"valid": True, "data": trip_data})


def get_trips(request):
    data = []
    trips = (
        Base_Trip.active.select_related("unplanned_trip")
        .select_related("planned_trip")
        .all()
    )
    for t in trips:
        if hasattr(t, "unplanned_trip"):
            data.append(t.unplanned_trip.summary())
        elif hasattr(t, "planned_trip"):
            data.append(t.planned_trip.summary())

    return JsonResponse({"valid": True, "data": data})


def get_destinations(request):
    data = json.loads(request.body)
    searchText = data["searchText"]
    destinations = Destination.objects.filter(
        Q(destination_name__icontains=searchText)
        | Q(destination_country__icontains=searchText)
    )[:20]
    data = []

    if searchText == "":
        return JsonResponse(
            {
                "valid": "True",
                "message": "Destinatiosn Fecthed None",
                "destinations": data,
            }
        )
    for d in destinations:
        data.append(d.summary())
    return JsonResponse(
        {"valid": "True", "message": "Destinatiosn Fecthed", "destinations": data}
    )


def create_default_destinations(request):
    data = json.loads(request.body)
    destinations = data["destinations"]

    for d in destinations:
        Destination.create_destination(d)
    return JsonResponse({"valid": True, "message": "Destinations Created"})
