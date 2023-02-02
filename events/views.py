from django.http import JsonResponse
import json
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.utils.dateparse import parse_datetime, parse_duration
from events.models import (
    Air_travel,
    Car_travel,
    Unplanned_activity,
    Planned_activity,
    Location,
    Lodging,
    Base_event,
)

from trips.models import Base_Trip

# Create your views here.
@login_required
@transaction.atomic
def create_planned_event(request):
    data = json.loads(request.body)
    user_extension = request.user.profile
    trip_uuid = data["trip_uuid"]
    trip = Base_Trip.active.select_related("trip_owner").get(_trip_uuid=trip_uuid)

    authorized_users_by_uuid = trip.authorized_users.all().in_bulk(
        field_name="_user_uuid"
    )
    authorized_user = authorized_users_by_uuid.get(user_extension._user_uuid, None)

    if authorized_user or user_extension == trip.trip_owner:
        start_time = parse_datetime(data["start_time"])
        end_time = parse_datetime(data["end_time"])
        planned_activity = Planned_activity(start_time=start_time, end_time=end_time)
        setattr(planned_activity, "user_added", user_extension)
        planned_activity.populate_values(data, user_extension)

        return JsonResponse(
            {
                "valid": True,
                "message": "Event Created",
                "reponse": planned_activity.summary(),
            }
        )
    else:
        return JsonResponse(
            {
                "valid": False,
                "message": "Can't create planned event in unplanned trip",
            }
        )


@login_required
@transaction.atomic
def create_unplanned_event(request):
    data = json.loads(request.body)
    user_extension = request.user.profile
    trip_uuid = data["trip_uuid"]
    trip = Base_Trip.active.select_related("trip_owner").get(_trip_uuid=trip_uuid)

    authorized_users_by_uuid = trip.authorized_users.all().in_bulk(
        field_name="_user_uuid"
    )
    authorized_user = authorized_users_by_uuid.get(user_extension._user_uuid, None)

    if authorized_user or user_extension == trip.trip_owner:
        unplanned_activity = Unplanned_activity()
        setattr(unplanned_activity, "user_added", user_extension)
        unplanned_activity.populate_values(data, user_extension)
        return JsonResponse(
            {
                "valid": True,
                "message": "Event Created",
                "reponse": unplanned_activity.summary(),
            }
        )


@login_required
@transaction.atomic
def create_air_travel(request):
    data = json.loads(request.body)
    user_extension = request.user.profile
    flight_origin = data["flight_origin"]
    flight_destination = data["flight_destination"]
    trip_uuid = data["trip_uuid"]
    trip = Base_Trip.active.select_related("trip_owner").get(_trip_uuid=trip_uuid)

    authorized_users_by_uuid = trip.authorized_users.all().in_bulk(
        field_name="_user_uuid"
    )
    authorized_user = authorized_users_by_uuid.get(user_extension._user_uuid, None)

    if authorized_user or user_extension == trip.trip_owner:
        air_travel = Air_travel(
            flight_origin=flight_origin, flight_destination=flight_destination
        )
        if "flight_number" in data:
            flight_number = data["flight_number"]
            setattr(air_travel, "flight_number", flight_number)
        if "start_time" in data:
            start_time = parse_datetime(data["start_time"])
            setattr(air_travel, "start_time", start_time)

        if "end_time" in data:
            end_time = parse_datetime(data["end_time"])
            setattr(air_travel, "end_time", end_time)

        setattr(air_travel, "user_added", user_extension)
        air_travel.populate_values(data, user_extension)
        return JsonResponse(
            {
                "valid": True,
                "message": "Event Created",
                "reponse": air_travel.summary(),
            }
        )


@login_required
@transaction.atomic
def create_car_travel(request):
    data = json.loads(request.body)
    user_extension = request.user.profile
    trip_uuid = data["trip_uuid"]
    trip = Base_Trip.active.select_related("trip_owner").get(_trip_uuid=trip_uuid)
    authorized_users_by_uuid = trip.authorized_users.all().in_bulk(
        field_name="_user_uuid"
    )
    authorized_user = authorized_users_by_uuid.get(user_extension._user_uuid, None)

    starting_location_id = data["starting_location_id"]
    starting_location = Location.objects.get(place_id=starting_location_id)
    ending_location_id = data["ending_location_id"]
    ending_location = Location.objects.get(place_id=ending_location_id)

    if authorized_user or user_extension == trip.trip_owner:
        car_travel = Car_travel(
            starting_location=starting_location, ending_location=ending_location
        )
        if "confirmation" in data:
            confirmation = data["confirmation"]
            setattr(car_travel, "confirmation", confirmation)

        setattr(car_travel, "user_added", user_extension)
        car_travel.populate_values(data, user_extension)
        return JsonResponse(
            {
                "valid": True,
                "message": "Event Created",
                "reponse": car_travel.summary(),
            }
        )


@login_required
@transaction.atomic
def create_lodging(request):
    data = json.loads(request.body)
    user_extension = request.user.profile
    trip_uuid = data["trip_uuid"]
    trip = Base_Trip.active.select_related("trip_owner").get(_trip_uuid=trip_uuid)

    authorized_users_by_uuid = trip.authorized_users.all().in_bulk(
        field_name="_user_uuid"
    )
    authorized_user = authorized_users_by_uuid.get(user_extension._user_uuid, None)

    if authorized_user or user_extension == trip.trip_owner:
        location_id = data["location_id"]
        location = Location.objects.get(place_id=location_id)
        lodging = Lodging(location=location)

        if "confirmation" in data:
            confirmation = data["confirmation"]
            setattr(lodging, "confirmation", confirmation)

        setattr(lodging, "user_added", user_extension)
        lodging.populate_values(data, user_extension)
        return JsonResponse(
            {
                "valid": True,
                "message": "Event Created",
                "reponse": lodging.summary(),
            }
        )


@login_required
@transaction.atomic
def create_location(request):
    data = json.loads(request.body)
    location = Location().populate_values(data)
    return JsonResponse(
        {
            "valid": True,
            "message": "Location Created",
            "response": location.summary(),
        }
    )


@login_required
@transaction.atomic
def delete_event(request):
    data = json.loads(request.body)
    user_extension = request.user.profile
    event_uuid = data["event_uuid"]
    event = Base_event.objects.get(_event_uuid=event_uuid)
    trip_uuid = data["trip_uuid"]
    trip = Base_Trip.active.select_related("trip_owner").get(_trip_uuid=trip_uuid)

    authorized_users_by_uuid = trip.authorized_users.all().in_bulk(
        field_name="_user_uuid"
    )
    authorized_user = authorized_users_by_uuid.get(user_extension._user_uuid, None)

    if (
        authorized_user
        or user_extension == trip.trip_owner
        or user_extension == event.user_added
    ):
        setattr(event, "is_deleted", True)
        event.save()
        return JsonResponse(
            {"valid": True, "message": "Event Deleted", "response": event.summary()}
        )
    else:
        return JsonResponse(
            {
                "valid": False,
                "message": "Not an authorized user ",
            }
        )


@login_required
@transaction.atomic
def reactivate_event(request):
    data = json.loads(request.body)
    user_extension = request.user.profile
    event_uuid = data["event_uuid"]
    event = Base_event.objects.get(_event_uuid=event_uuid)
    trip = event.trip

    authorized_users_by_uuid = trip.authorized_users.all().in_bulk(
        field_name="_user_uuid"
    )
    authorized_user = authorized_users_by_uuid.get(user_extension._user_uuid, None)

    if (
        authorized_user
        or user_extension == trip.trip_owner
        or user_extension == event.user_added
    ):
        setattr(event, "is_deleted", False)
        event.save()
        return JsonResponse(
            {"valid": True, "message": "Event Deleted", "response": event.summary()}
        )
    else:
        return JsonResponse(
            {
                "valid": False,
                "message": "Not an authorized user ",
            }
        )


@login_required
@transaction.atomic
def update_generic_event(request):
    data = json.loads(request.body)
    user_extension = request.user.profile
    event_uuid = data["event_uuid"]
    base_event = (
        Base_event.active.select_related("generic_activity__planned_activity")
        .select_related("generic_activity__unplanned_activity")
        .get(_event_uuid=event_uuid)
    )

    if hasattr(base_event, "generic_activity"):
        activity = base_event.generic_activity
        if hasattr(activity, "planned_activity"):
            event = Planned_activity.objects.get(_event_uuid=event_uuid)
        elif hasattr(activity, "unplanned_activity"):
            event = Unplanned_activity.objects.get(_event_uuid=event_uuid)

    authorized_users_by_uuid = event.trip.authorized_users.all().in_bulk(
        field_name="_user_uuid"
    )
    authorized_user = authorized_users_by_uuid.get(user_extension._user_uuid, None)

    UPDATE_FIELDS = [
        "start_time",
        "end_time",
    ]

    if (
        authorized_user
        or user_extension == event.trip.trip_owner
        or user_extension == event.user_added
    ):
        event.populate_values(data, user_extension)
        for atr in UPDATE_FIELDS:
            if atr in data:
                if atr == "start_time" or atr == "end_time":
                    parsed_value = parse_datetime(data[atr])
                    setattr(event, atr, parsed_value)
                elif atr == "alert_time":
                    parsed_value = parse_duration(data[atr])
                    setattr(event, atr, parsed_value)
                else:
                    setattr(event, atr, data[atr])

        event.save()
        return JsonResponse(
            {"valid": True, "message": "Event Updated", "response": event.summary()}
        )


@login_required
@transaction.atomic
def update_air_travel(request):
    data = json.loads(request.body)
    user_extension = request.user.profile
    event_uuid = data["event_uuid"]
    event = Air_travel.objects.get(_event_uuid=event_uuid)
    authorized_users_by_uuid = event.trip.authorized_users.all().in_bulk(
        field_name="_user_uuid"
    )
    authorized_user = authorized_users_by_uuid.get(user_extension._user_uuid, None)

    UPDATE_FIELDS = [
        "start_time",
        "end_time",
        "flight_number",
        "flight_origin",
        "fight-destination",
        "confirmation",
    ]
    if (
        authorized_user
        or user_extension == event.trip.trip_owner
        or user_extension == event.user_added
    ):
        event.populate_values(data, user_extension)
        for atr in UPDATE_FIELDS:
            if atr in data:
                if atr == "start_time" or atr == "end_time":
                    parsed_value = parse_datetime(data[atr])
                    setattr(event, atr, parsed_value)
                else:
                    setattr(event, atr, data[atr])

        event.save()
        return JsonResponse(
            {"valid": True, "message": "Event Updated", "response": event.summary()}
        )


@login_required
@transaction.atomic
def update_car_travel(request):
    data = json.loads(request.body)
    user_extension = request.user.profile
    event_uuid = data["event_uuid"]
    event = Car_travel.objects.get(_event_uuid=event_uuid)

    UPDATE_FIELDS = [
        "start_time",
        "end_time",
        "starting_location",
        "ending_location",
        "confirmation",
    ]

    authorized_users_by_uuid = event.trip.authorized_users.all().in_bulk(
        field_name="_user_uuid"
    )
    authorized_user = authorized_users_by_uuid.get(user_extension._user_uuid, None)

    if (
        authorized_user
        or user_extension == event.trip.trip_owner
        or user_extension == event.user_added
    ):
        event.populate_values(data, user_extension)
        for atr in UPDATE_FIELDS:
            if atr in data:
                if atr == "start_time" or atr == "end_time":
                    parsed_value = parse_datetime(data[atr])
                    setattr(event, atr, parsed_value)
                elif atr == "starting_location" or atr == "ending_location":
                    location_id = data[atr]
                    location = Location.objects.get(place_id=location_id)
                    setattr(event, atr, location)
                else:
                    setattr(event, atr, data[atr])

        event.save()
        return JsonResponse(
            {"valid": True, "message": "Event Updated", "response": event.summary()}
        )
    else:
        return JsonResponse({"valid": False, "message": "Not allowed"})


@login_required
@transaction.atomic
def update_lodging(request):
    data = json.loads(request.body)
    user_extension = request.user.profile
    event_uuid = data["event_uuid"]
    event = Lodging.objects.get(_event_uuid=event_uuid)
    UPDATE_FIELDS = [
        "start_time",
        "end_time",
        "location",
        "confirmation",
    ]
    authorized_users_by_uuid = event.trip.authorized_users.all().in_bulk(
        field_name="_user_uuid"
    )
    authorized_user = authorized_users_by_uuid.get(user_extension._user_uuid, None)

    if (
        authorized_user
        or user_extension == event.trip.trip_owner
        or user_extension == event.user_added
    ):
        event.populate_values(data, user_extension)
        for atr in UPDATE_FIELDS:
            if atr in data:
                if atr == "start_time" or atr == "end_time":
                    parsed_value = parse_datetime(data[atr])
                    setattr(event, atr, parsed_value)
                elif atr == "location":
                    location_id = data[atr]
                    location = Location.objects.get(place_id=location_id)
                    setattr(event, atr, location)
                else:
                    setattr(event, atr, data[atr])

        event.save()
        return JsonResponse(
            {"valid": True, "message": "Event Updated", "response": event.summary()}
        )


def google_places_api():
    pass


def airline_api():
    pass


def get_all_events(request):
    data = {}
    data["planned"] = [e.summary() for e in Planned_activity.objects.all()]
    data["unplanned"] = [e.summary() for e in Unplanned_activity.objects.all()]
    data["car"] = [e.summary() for e in Car_travel.objects.all()]
    data["air"] = [e.summary() for e in Air_travel.objects.all()]
    data["lodging"] = [e.summary() for e in Lodging.objects.all()]
    return JsonResponse({"valid": True, "response": data})
