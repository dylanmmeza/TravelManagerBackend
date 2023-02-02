from django.urls import path

from . import views

urlpatterns = [
    path("get_user_profile/", views.get_user_profile, name="get_user_profile"),
    path("get_users/", views.get_users, name="users"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout, name="logout"),
    path("auth_login/", views.auth_login, name="auth_login"),
    path("sign_up/", views.sign_up, name="sign_up"),
    path("update_user/", views.update_user, name="update_user"),
    path("soft_delete/", views.soft_delete, name="soft_delete"),
    path("my_friends/", views.my_friends, name="my_friends"),
    path("add_friend/", views.add_friend, name="add_friend"),
    path("remove_friend/", views.remove_friend, name="remove_friend"),
]
