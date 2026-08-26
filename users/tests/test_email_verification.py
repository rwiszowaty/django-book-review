import pytest

from allauth.account.models import EmailAddress
from django.conf import settings
from django.urls import reverse


def test_email_verification_is_mandatory():
    assert settings.ACCOUNT_EMAIL_VERIFICATION == "mandatory"


@pytest.mark.django_db
def test_registration_creates_email_address(registered_user):
    email_address = EmailAddress.objects.get(
        email=registered_user.email,
    )

    assert email_address.email == registered_user.email
    assert email_address.verified is False
    assert email_address.primary is True


@pytest.mark.django_db
def test_registration_sends_verification_email(
    verification_email, verification_signup_data
):
    email = verification_email

    assert email.to == [
        verification_signup_data["email"],
    ]

    assert "Confirm" in email.subject


@pytest.mark.django_db
def test_verification_email_contains_confirmation_link(verification_email):
    email = verification_email

    assert "/accounts/confirm-email/" in email.body


@pytest.mark.django_db
def test_user_can_confirm_email(client, confirmation_url, verification_signup_data):
    email_address = EmailAddress.objects.get(
        email=verification_signup_data["email"],
    )

    assert email_address.verified is False

    response = client.get(confirmation_url)

    assert response.status_code == 200

    response = client.post(confirmation_url)

    assert response.status_code == 302

    email_address.refresh_from_db()

    assert email_address.verified is True


@pytest.mark.django_db
def test_invalid_confirmation_link_does_not_verify_email(
    client, verification_signup_data
):
    client.post(
        reverse("account_signup"),
        verification_signup_data,
    )

    email_address = EmailAddress.objects.get(email=verification_signup_data["email"])

    assert email_address.verified is False

    response = client.get(
        "/accounts/confirm-email/invalid-key/",
    )

    assert response.status_code == 200

    email_address.refresh_from_db()

    assert email_address.verified is False
