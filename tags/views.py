import json
from django.http import JsonResponse
from django.db import transaction
from django.contrib.auth.decorators import login_required

from events.models import Base_event
from tags.models import BaseTag, EventTag, TripTag, TripTagUsage, EventTagUsage
from trips.models import Base_Trip


# Create/Delete Base Trip/Event Tags
@transaction.atomic
def create_trip_tag(request):
    data = json.loads(request.body)
    trip_tag = TripTag()
    trip_tag.populate_values(data)
    return JsonResponse(
        {
            "valid": True,
            "message": "Trip Tag Created",
            "reponse": trip_tag.summary(),
        }
    )


@transaction.atomic
def create_event_tag(request):
    data = json.loads(request.body)
    event_tag = EventTag()
    event_tag.populate_values(data)
    return JsonResponse(
        {
            "valid": True,
            "message": "Event Tag Created",
            "reponse": event_tag.summary(),
        }
    )


# Create Trip/Event Tag Usages
@login_required
@transaction.atomic
def create_trip_tag_usage(request):
    data = json.loads(request.body)
    user_extension = request.user.profile
    trip_tag = TripTag.objects.get(_tag_uuid=data["tag_uuid"])
    trip_uuid = data["trip_uuid"]
    trip = Base_Trip.active.select_related("trip_owner").get(_trip_uuid=trip_uuid)

    authorized_users_by_uuid = trip.authorized_users.all().in_bulk(
        field_name="_user_uuid"
    )
    authorized_user = authorized_users_by_uuid.get(user_extension._user_uuid, None)

    if user_extension == trip.trip_owner or authorized_user:
        triptagusage = TripTagUsage.objects.create(
            trip=trip,
            trip_tag=trip_tag,
            tag_creator=user_extension,
            last_updated_by=user_extension,
            value=data["value"],
            is_active=True,
        )
        triptagusage.save()
        return JsonResponse(
            {
                "valid": True,
                "message": "Trip Tag Usage Created",
                "response": triptagusage.summary(),
            }
        )
    else:
        return JsonResponse({"valid": False, "message": "Not Authorized User"})


@login_required
@transaction.atomic
def create_event_tag_usage(request):
    data = json.loads(request.body)
    user_extension = request.user.profile
    event_tag = EventTag.objects.get(_tag_uuid=data["tag_uuid"])
    event_uuid = data["event_uuid"]
    event = (
        Base_event.active.select_related("user_added")
        .select_related("trip")
        .get(_event_uuid=event_uuid)
    )

    authorized_users_by_uuid = event.trip.authorized_users.all().in_bulk(
        field_name="_user_uuid"
    )

    authorized_user = authorized_users_by_uuid.get(user_extension._user_uuid, None)

    if user_extension == event.trip.trip_owner or authorized_user:
        eventtagusage = EventTagUsage.objects.create(
            event=event,
            event_tag=event_tag,
            tag_creator=user_extension,
            last_updated_by=user_extension,
            value=data["value"],
            is_active=True,
        )
        eventtagusage.save()
        return JsonResponse(
            {
                "valid": True,
                "message": "Event Tag Usage Created",
                "response": eventtagusage.summary(),
            }
        )
    else:
        return JsonResponse({"valid": False, "message": "Not Authorized User"})


# Update Trip/Event Tag Usages
@login_required
@transaction.atomic
def update_trip_tag_usage(request):
    data = json.loads(request.body)
    user_extension = request.user.profile
    tag_uuid = data["tag_uuid"]
    trip_tag = TripTag.objects.get(_tag_uuid=tag_uuid)
    trip_uuid = data["trip_uuid"]
    trip = Base_Trip.active.select_related("trip_owner").get(_trip_uuid=trip_uuid)
    authorized_users_by_uuid = trip.authorized_users.all().in_bulk(
        field_name="_user_uuid"
    )
    authorized_user = authorized_users_by_uuid.get(user_extension._user_uuid, None)
    trip_tag_usage = TripTagUsage.objects.get(trip_tag=trip_tag, trip=trip)

    if user_extension == trip.trip_owner or authorized_user:
        if "value" in data:
            setattr(trip_tag_usage, "value", data["value"])
            setattr(trip_tag_usage, "last_updated_by", user_extension)
        if "is_active" in data:
            setattr(trip_tag_usage, "is_active", data["is_active"])

        trip_tag_usage.save()
        return JsonResponse({"valid": True, "response": "Tag Usage Updated"})
    else:
        return JsonResponse({"valid": False, "message": "Not allowed user"})


@login_required
@transaction.atomic
def update_event_tag_usage(request):
    data = json.loads(request.body)
    user_extension = request.user.profile
    tag_uuid = data["tag_uuid"]
    event_tag = EventTag.objects.get(_tag_uuid=tag_uuid)
    event_uuid = data["event_uuid"]
    event = (
        Base_event.active.select_related("user_added")
        .select_related("trip")
        .get(_event_uuid=event_uuid)
    )
    event_tag_usage = EventTagUsage.objects.get(event_tag=event_tag, event=event)

    authorized_users_by_uuid = event.trip.authorized_users.all().in_bulk(
        field_name="_user_uuid"
    )

    authorized_user = authorized_users_by_uuid.get(user_extension._user_uuid, None)

    if user_extension == event.trip.trip_owner or authorized_user:
        if "value" in data:
            setattr(event_tag_usage, "value", data["value"])
            setattr(event_tag_usage, "last_updated_by", user_extension)
        if "is_active" in data:
            setattr(event_tag_usage, "is_active", data["is_active"])

        event_tag_usage.save()
        return JsonResponse({"valid": True, "response": "Tag Usage Updated"})
    else:
        return JsonResponse({"valid": False, "message": "Not allowed user"})


# Delete Trip/Event Tag Usages
@login_required
@transaction.atomic
def delete_trip_tag_usage(request):
    data = json.loads(request.body)
    tag_uuid = data["tag_uuid"]
    user_extension = request.user.profile
    trip_tag_usage = (
        TripTagUsage.objects.select_related("tag_creator")
        .prefetch_related("trip")
        .get(trip_tag___tag_uuid=tag_uuid)
    )
    trip = trip_tag_usage.trip
    authorized_users_by_uuid = trip.authorized_users.all().in_bulk(
        field_name="_user_uuid"
    )
    authorized_user = authorized_users_by_uuid.get(user_extension._user_uuid, None)
    if (
        user_extension == trip_tag_usage.tag_creator
        or user_extension == trip.trip_owner
        or authorized_user
    ):
        setattr(trip_tag_usage, "is_active", False)
        setattr(trip_tag_usage, "last_update_by", user_extension)
        trip_tag_usage.save()
        return JsonResponse(
            {
                "valid": True,
                "message": "Trip Tag Deleted",
                "trip": trip_tag_usage.summary(),
            }
        )
    else:
        return JsonResponse({"valid": False, "message": "Not allowed"})


@login_required
@transaction.atomic
def delete_event_tag_usage(request):
    data = json.loads(request.body)
    tag_uuid = data["tag_uuid"]
    user_extension = request.user.profile
    event_tag_usage = (
        EventTagUsage.objects.select_related("tag_creator")
        .prefetch_realted("event")
        .get(event_tag___tag_uuid=tag_uuid)
    )
    event = event_tag_usage.trip
    authorized_users_by_uuid = event.trip.authorized_users.all().in_bulk(
        field_name="_user_uuid"
    )
    authorized_user = authorized_users_by_uuid.get(user_extension._user_uuid, None)
    if (
        user_extension == event_tag_usage.tag_creator
        or user_extension == event.trip_owner
        or authorized_user
    ):
        setattr(event_tag_usage, "is_active", False)
        setattr(event_tag_usage, "last_update_by", user_extension)
        event_tag_usage.save()
        return JsonResponse(
            {
                "valid": True,
                "message": "Trip Tag Deleted",
                "trip": event_tag_usage.summary(),
            }
        )
    else:
        return JsonResponse({"valid": False, "message": "Not allowed"})


def get_trip_tag_usages(request):
    data = json.loads(request.body)
    tag_data = []
    trip_uuid = data["trip_uuid"]
    trip = Base_Trip.active.get(_trip_uuid=trip_uuid)
    trip_tags = TripTagUsage.objects.filter(trip=trip)
    for tag in trip_tags:
        tag_data.append(tag.summary())
    return JsonResponse({"valid": True, "response": tag_data})


def get_event_tag_usages(request):
    data = json.loads(request.body)
    tag_data = []
    event_uuid = data["event_uuid"]
    event = Base_event.active.get(_event_uuid=event_uuid)
    event_tags = EventTagUsage.objects.filter(event=event)
    for t in event_tags:
        tag_data.append(t.summary())

    return JsonResponse({"valid": True, "response": tag_data})


def get_base_tags(request):
    data = []
    tags = BaseTag.active.all()
    for t in tags:
        data.append(t.summary())
    return JsonResponse({"valid": True, "reponse": data})
