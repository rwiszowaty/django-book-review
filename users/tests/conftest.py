import pytest
import re

from django.urls import reverse
from django.core import mail
from allauth.account.models import EmailAddress

from books.models import Book, Review


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


@pytest.fixture
def verified_user(django_user_model, signup_data):
    user = django_user_model.objects.create_user(
        email=signup_data["email"],
        password=signup_data["password1"],
    )

    EmailAddress.objects.create(
        user=user, email=user.email, primary=True, verified=True
    )

    return user


@pytest.fixture
def login_data(signup_data):
    return {
        "login": signup_data["email"],
        "password": signup_data["password1"],
    }


@pytest.fixture
def user_with_username(django_user_model):
    return django_user_model.objects.create(
        email="test@example.com",
        password="StrongPassword123!",
        username="Nickname",
    )


@pytest.fixture
def book():
    return Book.objects.create(
        title="The great hunt",
        slug="the-great-hunt",
        isbn="1234567890123",
    )


@pytest.fixture
def review(book, user_with_username):
    return Review.objects.create(
        book=book,
        user=user_with_username,
        content="Example of book review.",
        rating=5,
    )
