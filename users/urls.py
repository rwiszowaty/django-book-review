from django.urls import path

from .views import ProfileEditView, ProfileView, SetUsernameView

app_name = "users"


urlpatterns = [
    path("profile/", ProfileView.as_view(), name="profile"),
    path("profile/edit/", ProfileEditView.as_view(), name="profile_edit"),
    path("set-username/", SetUsernameView.as_view(), name="set_username"),
]
