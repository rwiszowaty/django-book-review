import pytest
import re

from django.urls import reverse
from django.core import mail


@pytest.fixture
def password_reset_data(verified_user):
    return {
        "email": verified_user.email,
    }


@pytest.fixture
def password_reset_email(client, password_reset_data):
    response = client.post(
        reverse("account_reset_password"),
        password_reset_data,
    )

    assert response.status_code == 302
    assert len(mail.outbox) == 1

    return mail.outbox[0]


@pytest.fixture
def password_reset_url(password_reset_email):
    match = re.search(
        r"/accounts/password/reset/key/\S+/",
        password_reset_email.body,
    )

    assert match is not None

    return match.group(0)


def test_password_reset_page_loads(client):
    response = client.get(reverse("account_reset_password"))

    assert response.status_code == 200


@pytest.mark.django_db
def test_password_reset_sends_email(password_reset_email, password_reset_data):
    assert password_reset_email.to == [password_reset_data["email"]]
    assert "Password Reset Email" in password_reset_email.subject


@pytest.mark.django_db
def test_password_reset_link_redirects_to_set_password(client, password_reset_url):
    response = client.get(password_reset_url)

    assert response.status_code == 302
    assert response.url.startswith("/accounts/password/reset/key/")
    assert response.url.endswith("-set-password/")


@pytest.mark.django_db
def test_password_reset_does_not_send_email_to_unknown(client):
    response = client.post(
        reverse("account_reset_password"),
        {
            "email": "unknown@example.com",
        },
    )

    assert response.status_code == 302
    assert len(mail.outbox) == 0


@pytest.mark.django_db
def test_user_can_reset_password(
    client, password_reset_url, signup_data, django_user_model
):
    user = django_user_model.objects.get(
        email=signup_data["email"],
    )

    response = client.get(password_reset_url)

    assert response.status_code == 302

    new_password = "NewStrongPassword123!"

    response = client.post(
        response.url,
        {
            "password1": new_password,
            "password2": new_password,
        },
    )

    assert response.status_code == 302
    assert response.url == "/accounts/password/reset/key/done/"

    user.refresh_from_db()

    assert user.check_password(new_password)
    assert not user.check_password(signup_data["password1"])


@pytest.mark.django_db
def test_password_reset_rejects_mismatched_passwords(client, password_reset_url):
    response = client.get(password_reset_url)

    assert response.status_code == 302

    response = client.post(
        response.url,
        {
            "password1": "NewStrongPassword123!",
            "password2": "DifferentPassword123!",
        },
    )

    assert response.status_code == 200
    assert not response.context["form"].is_valid()


@pytest.mark.django_db
def test_password_reset_link_cannot_be_reused(
    client, password_reset_url, password_reset_data, django_user_model
):
    user = django_user_model.objects.get(
        email=password_reset_data["email"],
    )

    response = client.get(password_reset_url)

    assert response.status_code == 302

    new_password = "NewStrongPassword123!"

    response = client.post(
        response.url,
        {
            "password1": new_password,
            "password2": new_password,
        },
    )

    assert response.status_code == 302

    user.refresh_from_db()

    assert user.check_password(new_password)

    response = client.get(password_reset_url)

    assert response.status_code == 200
