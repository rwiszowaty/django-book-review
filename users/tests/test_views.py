import pytest
from django.urls import reverse

from users.forms import UsernameForm


@pytest.mark.django_db
class TestSetUsernameView:
    def test_authenticated_user_can_access_view(
        self,
        client,
        registered_user,
    ):
        client.force_login(registered_user)

        response = client.get(
            reverse("users:set_username"),
        )

        assert response.status_code == 200
        assert isinstance(
            response.context["form"],
            UsernameForm,
        )

    def test_anonymous_user_cannot_access_view(
        self,
        client,
    ):
        response = client.get(
            reverse("users:set_username"),
        )

        assert response.status_code == 302
        assert "accounts/login/" in response.url

    def test_user_can_set_username(
        self,
        client,
        registered_user,
        django_user_model,
    ):
        client.force_login(registered_user)

        response = client.post(
            reverse("users:set_username"),
            {
                "username": "Nickname",
            },
        )

        assert response.status_code == 302
        assert response.url == reverse("books:book_list")

        registered_user.refresh_from_db()

        assert registered_user.username == "Nickname"
