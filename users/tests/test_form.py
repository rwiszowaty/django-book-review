import pytest

from allauth.account.models import EmailAddress
from users.forms import CustomAddEmailForm


@pytest.mark.django_db
def test_add_email_form_rejects_existing_email(
    verified_user,
    django_user_model,
):
    other_user = django_user_model.objects.create_user(
        email="test2@example.com",
        password="StrongPassword123!",
    )

    EmailAddress.objects.create(
        user=other_user,
        email=other_user.email,
        primary=True,
        verified=True,
    )

    form = CustomAddEmailForm(
        data={"email": other_user.email},
        user=verified_user,
    )

    assert not form.is_valid()
    assert "email" in form.errors


@pytest.mark.django_db
def test_add_email_form_accepts_new_email(
    verified_user,
):
    form = CustomAddEmailForm(
        data={"email": "new.email@example.com"},
        user=verified_user,
    )

    assert form.is_valid()
    assert form.cleaned_data["email"] == "new.email@example.com"


@pytest.mark.django_db
def test_add_email_form_rejects_users_own_email(
    verified_user,
):
    form = CustomAddEmailForm(
        data={"email": verified_user.email},
        user=verified_user,
    )

    assert not form.is_valid()
    assert "email" in form.errors
