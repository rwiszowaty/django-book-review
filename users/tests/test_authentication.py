import pytest

from django.urls import reverse
from allauth.account.models import EmailAddress


@pytest.mark.django_db
def test_user_can_login(client, verified_user, login_data):
    response = client.post(
        reverse("account_login"),
        login_data,
    )

    assert response.status_code == 302
    assert response.wsgi_request.user.is_authenticated
    assert response.wsgi_request.user == verified_user


@pytest.mark.django_db
def test_user_cannot_login_with_wrong_password(client, verified_user, login_data):
    data = login_data.copy()
    data["password"] = "WrongPassword123!"

    response = client.post(
        reverse("account_login"),
        data,
    )

    assert response.status_code == 200
    assert not response.wsgi_request.user.is_authenticated


@pytest.mark.django_db
def test_cannot_login_with_non_existent_user(client, login_data):
    data = login_data.copy()
    data["login"] = "unknown@example.com"

    response = client.post(
        reverse("account_login"),
        data,
    )

    assert response.status_code == 200
    assert not response.wsgi_request.user.is_authenticated


@pytest.mark.django_db
def test_unverified_user_cannot_login(client, registered_user, login_data):
    email_address = EmailAddress.objects.get(
        user=registered_user,
        email=registered_user.email,
    )

    assert email_address.verified is False

    response = client.post(
        reverse("account_login"),
        login_data,
    )

    assert response.status_code == 302
    assert response.url == "/accounts/confirm-email/"
    assert not response.wsgi_request.user.is_authenticated


@pytest.mark.django_db
def test_user_logout(client, verified_user, login_data):
    client.post(
        reverse("account_login"),
        login_data,
    )

    assert client.session.get("_auth_user_id") is not None

    response = client.post(
        reverse("account_logout"),
    )

    assert response.status_code == 302
    assert client.session.get("_auth_user_id") is None


@pytest.mark.django_db
def test_anonymous_user_can_logout(client):
    response = client.post(
        reverse("account_logout"),
    )

    assert response.status_code == 302


@pytest.mark.django_db
def test_user_is_authenticated_after_login(client, verified_user, login_data):
    client.post(
        reverse("account_login"),
        login_data,
    )

    response = client.get(
        reverse("account_login"),
    )

    assert response.wsgi_request.user.is_authenticated
    assert response.wsgi_request.user == verified_user


@pytest.mark.django_db
def test_user_is_anonymous_after_logout(client, verified_user, login_data):
    client.post(reverse("account_login"), login_data)

    client.post(
        reverse("account_logout"),
    )

    response = client.get(reverse("account_login"))

    assert not response.wsgi_request.user.is_authenticated


@pytest.mark.django_db
def test_session_is_persisted_between_requests(client, verified_user, login_data):
    response = client.post(
        reverse("account_login"),
        login_data,
    )

    assert response.status_code == 302

    response = client.get(reverse("account_login"))

    assert response.wsgi_request.user.is_authenticated
    assert response.wsgi_request.user == verified_user
