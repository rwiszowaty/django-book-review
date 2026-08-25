import pytest
import re

from django.urls import reverse
from django.core import mail


@pytest.fixture
def signup_data():
    return {
        "email": "test@example.com",
        "password1": "StrongPassword123!",
        "password2": "StrongPassword123!",
    }


# Allauth has rate limits so we use diffrent addresses
# to test confirmations emails
@pytest.fixture
def verification_signup_data(request):
    return {
        "email": f"verification-{request.node.name}@example.com",
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


@pytest.fixture
def verification_email(client, verification_signup_data):
    client.post(
        reverse("account_signup"),
        verification_signup_data,
    )

    assert len(mail.outbox) == 1

    return mail.outbox[0]


@pytest.fixture
def confirmation_url(verification_email):
    match = re.search(
        r"/accounts/confirm-email/\S+",
        verification_email.body,
    )

    assert match is not None

    return match.group(0)
