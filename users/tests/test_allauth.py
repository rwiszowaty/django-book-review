import pytest

from allauth.account.forms import SignupForm
from allauth.account.models import EmailAddress
from django.conf import settings
from django.urls import reverse


def test_signup_form_contains_proper_fields():
    form = SignupForm()

    assert "email" in form.fields
    assert "password1" in form.fields
    assert "password2" in form.fields
    assert "username" not in form.fields


def test_allauth_login_method_is_email():
    assert settings.ACCOUNT_LOGIN_METHODS == {"email"}


def test_allauth_username_field_is_disabled():
    assert settings.ACCOUNT_USER_MODEL_USERNAME_FIELD is None


def test_allauth_signup_fields():
    assert settings.ACCOUNT_SIGNUP_FIELDS == {
        "email*",
        "password1*",
        "password2*",
    }


def test_email_verification_is_mandatory():
    assert settings.ACCOUNT_EMAIL_VERIFICATION == "mandatory"


@pytest.mark.django_db
def test_user_can_register_with_email(client, signup_data, django_user_model):

    response = client.post(
        reverse("account_signup"),
        signup_data,
    )

    assert response.status_code == 302

    assert django_user_model.objects.filter(email="test@example.com").exists()


@pytest.mark.django_db
def test_registered_user_password_is_hashed(registered_user, signup_data):
    assert registered_user.password != signup_data["password1"]
    assert registered_user.check_password(signup_data["password1"])


@pytest.mark.django_db
def test_registered_email_is_not_verified(registered_user):
    email_address = EmailAddress.objects.get(
        email="test@example.com",
    )

    assert email_address.verified is False


@pytest.mark.django_db
def test_registration_fails_when_password_do_not_match(
    client, signup_data, django_user_model
):
    signup_data["password2"] = ["DifferentPassword123!"]
    response = client.post(
        reverse("account_signup"),
        signup_data,
    )

    assert response.status_code == 200

    assert not django_user_model.objects.filter(
        email=signup_data["email"],
    ).exists()


@pytest.mark.django_db
def test_registration_fails_with_invalid_email(client, signup_data, django_user_model):
    signup_data["email"] = "not-an-email"
    response = client.post(
        reverse("account_signup"),
        signup_data,
    )

    assert response.status_code == 200

    assert not django_user_model.objects.filter(
        email=signup_data["email"],
    ).exists()
