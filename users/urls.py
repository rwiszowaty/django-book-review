from django.urls import path

from .views import ProfileView, SetUsernameView

app_name = "users"


urlpatterns = [
    path("profile/", ProfileView.as_view(), name="profile"),
    path("set-username/", SetUsernameView.as_view(), name="set_username"),
]
