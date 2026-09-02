from django.urls import path

from .views import SetUsernameView

app_name = "users"


urlpatterns = [
    path("set-username/", SetUsernameView.as_view(), name="set_username"),
]
