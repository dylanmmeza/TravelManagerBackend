import json
from django.http import JsonResponse
from django.db import transaction
from django.contrib.auth.decorators import login_required
from notifications.models import (
    Event_alert,
    Friend_request,
    Trip_request,
    General_Trip_Notification,
    Trip_Time_Alert,
)
from events.models import Base_event
from trips.models import Base_Trip
from users.models import User_extension


# TIME ALERTS
@transaction.atomic
def create_event_alert(request):
    data = json.loads(request.body)
    event_uuid = data["event_uuid"]
    recieving_user_uuid = data["recieving_user"]
    recieving_user = User_extension.active.get(_user_uuid=recieving_user_uuid)
    event = (
        Base_event.active.select_related("air_travel")
        .select_related("car_travel")
        .select_related("lodging")
        .select_related("generic_activity__planned_activity")
        .select_related("generic_activity__unplanned_activity")
        .get(_event_uuid=event_uuid)
    )

    event_alert = Event_alert(
        recieving_user=recieving_user,
        event=event,
    )
    event_alert.populate_values(data)
    return JsonResponse({"valid": True, "response": event_alert.summary()})


@transaction.atomic
def create_trip_alert(request):
    data = json.loads(request.body)
    trip_uuid = data["trip_uuid"]
    recieving_user_uuid = data["recieving_user"]
    recieving_user = User_extension.active.get(_user_uuid=recieving_user_uuid)
    trip = (
        Base_Trip.active.select_related("planned_trip")
        .select_related("unplanned_trip")
        .get(_trip_uuid=trip_uuid)
    )

    trip_alert = Trip_Time_Alert(
        recieving_user=recieving_user,
        trip=trip,
    )
    trip_alert.populate_values(data)
    return JsonResponse({"valid": True, "response": trip_alert.summary()})


# FRIEND REQUEST
@login_required
@transaction.atomic
def create_friend_request(request):
    data = json.loads(request.body)
    sending_user = request.user.profile
    recieving_user_uuid = data["recieving_user_uuid"]
    recieving_user = User_extension.active.get(_user_uuid=recieving_user_uuid)

    already_existing_request = Friend_request.active.filter(
        sending_user=sending_user, recieving_user=recieving_user
    )

    friends_by_uuid = sending_user.my_friends.all().in_bulk(field_name="_user_uuid")
    friend_match = friends_by_uuid.get(recieving_user._user_uuid, None)

    if (
        not friend_match
        and sending_user != recieving_user
        and not already_existing_request
    ):
        friend_request = Friend_request(
            sending_user=sending_user, recieving_user=recieving_user
        )
        friend_request.populate_values(data)
        return JsonResponse({"valid": True, "response": friend_request.summary()})
    else:
        return JsonResponse(
            {
                "valid": False,
                "message": "Already friends, receiver=self, or already created request",
            }
        )


@login_required
@transaction.atomic
def accept_friend_request(request):
    # Gather all neccesary info
    data = json.loads(request.body)
    user_extension = request.user.profile
    notification_uuid = data["notification_uuid"]
    friend_request = Friend_request.active.get(_notification_uuid=notification_uuid)
    sending_user = friend_request.sending_user
    recieving_user = friend_request.recieving_user

    # Check that the accepting user is correct user
    if recieving_user == user_extension:
        sending_user.my_friends.add(recieving_user)
        recieving_user.my_friends.add(sending_user)
        sending_user.save()
        recieving_user.save()
        friend_request.is_active = False
        friend_request.save()
        return JsonResponse({"valid": True, "response": "Friend Request Accepted"})
    else:
        return JsonResponse({"valid": True, "response": "Not Receiving User"})


@login_required
@transaction.atomic
def reject_friend_request(request):
    data = json.loads(request.body)
    user_extension = request.user.profile
    notification_uuid = data["notification_uuid"]
    friend_request = Friend_request.active.get(_notification_uuid=notification_uuid)
    if friend_request.recieving_user == user_extension:
        setattr(friend_request, "is_active", False)
        friend_request.save()
        return JsonResponse({"valid": True, "response": "Friend Request Rejected"})
    else:
        return JsonResponse({"valid": False, "response": "Not recieivng user"})


@login_required
@transaction.atomic
def cancel_friend_request(request):
    data = json.loads(request.body)
    user_extension = request.user.profile
    notification_uuid = data["notification_uuid"]
    friend_request = Friend_request.active.get(_notification_uuid=notification_uuid)
    if friend_request.sending_user == user_extension:
        setattr(friend_request, "is_active", False)
        friend_request.save()
        return JsonResponse({"valid": True, "response": "Friend Request Cancelled"})
    else:
        return JsonResponse({"valid": False, "response": "Not sending user"})


# TRIP REQUESTS
@login_required
@transaction.atomic
def create_trip_request(request):
    data = json.loads(request.body)
    sending_user = request.user.profile
    trip_uuid = data["trip_uuid"]
    trip = (
        Base_Trip.active.select_related("unplanned_trip")
        .select_related("planned_trip")
        .get(_trip_uuid=trip_uuid)
    )

    already_existing_request = Trip_request.active.filter(
        sending_user=sending_user, trip=trip
    )
    recieving_user = trip.trip_owner

    authorized_users_by_uuid = trip.authorized_users.all().in_bulk(
        field_name="_user_uuid"
    )
    authorized_user = authorized_users_by_uuid.get(sending_user._user_uuid, None)

    if (
        not authorized_user
        and sending_user != recieving_user
        and not already_existing_request
    ):
        trip_request = Trip_request(
            sending_user=sending_user, recieving_user=recieving_user, trip=trip
        )
        trip_request.populate_values(data)
        return JsonResponse({"valid": True, "response": trip_request.summary()})
    else:
        return JsonResponse(
            {
                "valid": False,
                "message": "Not authorized user, receiver=self, or already created request",
            }
        )


@login_required
@transaction.atomic
def accept_trip_request(request):
    # Gather all neccesary info
    data = json.loads(request.body)
    user_extension = request.user.profile
    notification_uuid = data["notification_uuid"]
    trip_request = Trip_request.active.get(_notification_uuid=notification_uuid)
    trip = trip_request.trip
    sending_user = trip_request.sending_user
    recieving_user = trip_request.recieving_user

    authorized_users_by_uuid = trip.authorized_users.all().in_bulk(
        field_name="_user_uuid"
    )
    authorized_user = authorized_users_by_uuid.get(user_extension._user_uuid, None)

    # Check that the accepting user is correct user
    if recieving_user == user_extension or authorized_user:
        trip.authorized_users.add(sending_user)
        trip.save()
        setattr(trip_request, "is_active", False)
        trip_request.save()
        return JsonResponse(
            {"valid": True, "response": "Trip Request Accepted. User added"}
        )
    else:
        return JsonResponse({"valid": True, "response": "Not Trip Owner"})


@login_required
@transaction.atomic
def reject_trip_request(request):
    data = json.loads(request.body)
    user_extension = request.user.profile
    notification_uuid = data["notification_uuid"]
    trip_request = Trip_request.active.get(_notification_uuid=notification_uuid)
    trip = trip_request.trip
    recieving_user = trip_request.recieving_user

    authorized_users_by_uuid = trip.authorized_users.all().in_bulk(
        field_name="_user_uuid"
    )
    authorized_user = authorized_users_by_uuid.get(user_extension._user_uuid, None)

    if recieving_user == user_extension or authorized_user:
        setattr(trip_request, "is_active", False)
        trip_request.save()
        return JsonResponse({"valid": True, "response": "Trip Request Rejected"})
    else:
        return JsonResponse({"valid": False, "response": "Not authorized user"})


@login_required
@transaction.atomic
def cancel_trip_request(request):
    data = json.loads(request.body)
    user_extension = request.user.profile
    notification_uuid = data["notification_uuid"]
    trip_request = Trip_request.active.get(_notification_uuid=notification_uuid)
    if trip_request.sending_user == user_extension:
        setattr(trip_request, "is_active", False)
        trip_request.save()
        return JsonResponse({"valid": True, "response": "Friend Request Cancelled"})
    else:
        return JsonResponse({"valid": False, "response": "Not sending user"})


# INFO NOTIFICATIONS
@login_required
@transaction.atomic
def create_general_trip_notification(request):
    # Can add type and get rid of trip related notification (1=Trip Change, 2=Friend Trip Created)
    data = json.loads(request.body)
    sending_user = request.user.profile
    trip_uuid = data["trip_uuid"]
    notification_type = data["notification_type"]
    recieving_user_uuid = data["recieving_user"]
    recieving_user = User_extension.active.get(_user_uuid=recieving_user_uuid)
    trip = (
        Base_Trip.active.select_related("unplanned_trip")
        .select_related("planned_trip")
        .get(_trip_uuid=trip_uuid)
    )

    general_trip_notification = General_Trip_Notification(
        sending_user=sending_user,
        recieving_user=recieving_user,
        trip=trip,
        notification_type=notification_type,
    )
    general_trip_notification.populate_values(data)
    return JsonResponse(
        {"valid": True, "response": general_trip_notification.summary()}
    )


@login_required
def unactivate_general_trip_notification(request):
    data = json.loads(request.body)
    user_extension = request.user.profile
    notification_uuid = data["notification_uuid"]
    general_trip_notification = General_Trip_Notification.active.get(
        _notification_uuid=notification_uuid
    )
    recieving_user = general_trip_notification.recieving_user
    if recieving_user == user_extension:
        setattr(general_trip_notification, "is_active", False)
        general_trip_notification.save()
        return JsonResponse(
            {"valid": True, "response": general_trip_notification.summary()}
        )


# MY NOTIFCATIONS
@login_required
@transaction.atomic
def get_notifications(request):
    notification_data = {}
    user_extension = request.user.profile

    notification_data["friend_requests"] = [
        f.summary() for f in Friend_request.active.filter(recieving_user=user_extension)
    ]
    notification_data["pending_friend_requests"] = [
        f.summary() for f in Friend_request.active.filter(sending_user=user_extension)
    ]
    notification_data["trip_requests"] = [
        t.summary() for t in Trip_request.active.filter(recieving_user=user_extension)
    ]
    notification_data["pending_trip_requests"] = [
        t.summary() for t in Trip_request.active.filter(sending_user=user_extension)
    ]
    notification_data["general_trip_notifications"] = [
        t.summary()
        for t in General_Trip_Notification.active.filter(recieving_user=user_extension)
    ]
    notification_data["event_alert"] = [
        t.summary() for t in Event_alert.active.filter(recieving_user=user_extension)
    ]
    notification_data["trip_alert"] = [
        t.summary()
        for t in Trip_Time_Alert.active.filter(recieving_user=user_extension)
    ]
    return JsonResponse({"valid": True, "reponse": notification_data})
