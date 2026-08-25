import pytest
from django.urls import reverse


@pytest.fixture
def signup_data():
    return {
        "email": "test@example.com",
        "password1": "StrongPassword123!",
        "password2": "StrongPassword123!",
    }


@pytest.fixture
def registered_user(client, django_user_model, signup_data):
    client.post(
        reverse("account_signup"),
        signup_data,
    )

    return django_user_model.objects.get(
        email=signup_data["email"],
    )
