import json
from django.db import transaction
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.http import JsonResponse

from users.models import User_extension

# Create your views here.


def login_view(request):
    data = json.loads(request.body)
    password_str = data["password"]
    username = data["username"]
    user_extension = User_extension.objects.filter(user__username=username)

    if user_extension:
        user_extension = user_extension[0]
        if user_extension.user.check_password(password_str):
            user_extension.is_deleted = False
            user_extension.save()
            login(request, user_extension.user)
            return JsonResponse(
                {
                    "valid": True,
                    "message": "Logged In and Created Cookie!",
                    "user": user_extension.summary(),
                }
            )
        else:
            return JsonResponse({"valid": False, "message": "Wrong Password!"})
    else:
        return JsonResponse({"valid": False, "message": "No Account"})


def sign_up(request):
    data = json.loads(request.body)
    username = data["username"]
    user_with_username = User_extension.objects.filter(user__username=username)
    if user_with_username:
        return JsonResponse({"valid": False, "message": "Username taken"})
    else:
        user_extension = User_extension.create_user(data)
        login_view(request)
        response = JsonResponse({"valid": True, "message": "User Created"})
        return response


@login_required
def auth_login(request):
    user_extension = request.user.profile
    return JsonResponse(
        {
            "valid": True,
            "message": "Authorized Session",
            "user": user_extension.summary(),
        }
    )


@login_required
def logout(request):
    # logout(request)
    response = JsonResponse({"valid": True, "message": "Logged Out"})
    response.delete_cookie("sessionid")
    return response


@login_required
@transaction.atomic
def update_user(request):
    data = json.loads(request.body)
    user = request.user
    user_extension = user.profile
    LIST_OF_USER_ATTRIBUTES = [
        "username",
        "first_name",
        "last_name",
        "email",
    ]
    for field in LIST_OF_USER_ATTRIBUTES:
        if field in data:
            if field == "username" and User_extension.active.filter(
                user__username=data[field]
            ):
                return JsonResponse({"valid": False, "message": "Username Taken "})
            else:
                setattr(user, field, data[field])
        user.save()

    LIST_OF_USER_EXT_ATTRIBUTES = ["date_of_birth", "bio"]
    for field in LIST_OF_USER_EXT_ATTRIBUTES:
        if field in data:
            if data[field] is not None:
                setattr(user_extension, field, data[field])
    user_extension.updated = datetime.now
    user_extension.save()

    return JsonResponse({"valid": True, "message": "Updated"})


@login_required
def soft_delete(request):
    user_extension = request.user.profile
    user_extension.is_deleted = True
    user_extension.save()
    response = JsonResponse({"valid": "True", "response": "User deleted"})
    response.delete_cookie("sessionid")
    return response


@login_required
def my_friends(request):
    user_extension = request.user.profile
    friend_data = [
        f.summary() for f in user_extension.my_friends.filter(is_deleted=False)
    ]
    return JsonResponse({"valid": "True", "friends": friend_data})


@login_required
@transaction.atomic
def add_friend(request):
    data = json.loads(request.body)
    friend_uuid = data["friend_uuid"]
    user_extension = request.user.profile
    friend = User_extension.active.get(_user_uuid=friend_uuid)

    friends_by_uuid = user_extension.my_friends.all().in_bulk(field_name="_user_uuid")
    friend_match = friends_by_uuid.get(user_extension._user_uuid, None)

    if friend_match or friend == user_extension:
        return JsonResponse(
            {"valid": "False", "response": "Friend Already Added (or self)"}
        )
    else:
        user_extension.my_friends.add(friend)
        friend.my_friends.add(user_extension)
        user_extension.save()
        friend.save()
        return JsonResponse({"valid": "True", "response": "Friend was added"})


@login_required
@transaction.atomic
def remove_friend(request):
    data = json.loads(request.body)
    friend_uuid = data["friend_uuid"]
    user_extension = request.user.profile
    friend = User_extension.active.get(_user_uuid=friend_uuid)

    friends_by_uuid = user_extension.my_friends.all().in_bulk(field_name="_user_uuid")
    friend_match = friends_by_uuid.get(user_extension._user_uuid, None)

    if not friend_match or friend == user_extension:
        return JsonResponse(
            {"valid": "False", "response": "Friend Already Removed (or self)"}
        )
    else:
        user_extension.my_friends.remove(friend)
        friend.my_friends.remove(user_extension)
        user_extension.save()
        friend.save()
        return JsonResponse({"valid": "True", "response": "Friend was added"})


@login_required
@transaction.atomic
def get_user_profile(request):
    user_extension = request.user.profile
    data = []
    data = [user_extension.user_details()]
    return JsonResponse({"valid": "True", "response": data})


# HELPER
def get_users(request):
    users = User_extension.objects.order_by("user__username")
    data = []
    for u in users:
        data.append(u.summary())
    return JsonResponse({"valid": "True", "response": data})
