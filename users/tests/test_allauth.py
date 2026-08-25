from allauth.account.forms import SignupForm
from django.conf import settings


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
