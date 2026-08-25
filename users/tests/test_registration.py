import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_user_can_register_with_email(client, signup_data, django_user_model):

    response = client.post(
        reverse("account_signup"),
        signup_data,
    )

    assert response.status_code == 302
    assert django_user_model.objects.filter(email=signup_data["email"]).exists()


@pytest.mark.django_db
def test_registered_user_has_correct_email(registered_user, signup_data):
    assert registered_user.email == signup_data["email"]


@pytest.mark.django_db
def test_registered_user_password_is_hashed(registered_user, signup_data):
    assert registered_user.password != signup_data["password1"]
    assert registered_user.check_password(signup_data["password1"])


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


@pytest.mark.django_db
def test_registration_does_not_create_duplicate_user(
    client,
    registered_user,
    signup_data,
    django_user_model,
):
    client.post(
        reverse("account_signup"),
        signup_data,
    )

    assert (
        django_user_model.objects.filter(
            email=signup_data["email"],
        ).count()
        == 1
    )
