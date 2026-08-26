import pytest
import re

from django.urls import reverse
from django.core import mail
from allauth.account.models import EmailAddress


@pytest.fixture(autouse=True)
def disable_allauth_rate_limits(settings):
    settings.ACCOUNT_RATE_LIMITS = False


@pytest.fixture
def email_change_data():
    return {
        "email": "new.email@example.com",
        "action_add": "Add",
    }


@pytest.fixture
def email_change_email_sent(client, verified_user, email_change_data):
    client.force_login(verified_user)

    response = client.post(
        reverse("account_email"),
        email_change_data,
    )

    assert response.status_code == 302
    assert len(mail.outbox) == 1

    return mail.outbox[0]


@pytest.fixture
def email_change_confirmation_url(email_change_email_sent):
    match = re.search(
        r"/accounts/confirm-email/\S+/",
        email_change_email_sent.body,
    )

    assert match is not None

    return match.group(0)


@pytest.mark.django_db
def test_email_change_page_loads(client, verified_user):
    client.force_login(verified_user)

    response = client.get(
        reverse("account_email"),
    )

    assert response.status_code == 200


@pytest.mark.django_db
def test_anonymous_user_cannot_change_email(client):
    response = client.get(
        reverse("account_email"),
    )

    assert response.status_code == 302
    assert response.url.startswith("/accounts/login/")


@pytest.mark.django_db
def test_email_change_email_is_sent_to_new_address(
    email_change_email_sent,
    email_change_data,
):

    assert email_change_email_sent.to == [email_change_data["email"]]
    assert "Confirm Your Email Address" in email_change_email_sent.subject


@pytest.mark.django_db
def test_email_change_does_not_change_email_before_confirmation(
    client,
    verified_user,
    email_change_data,
):
    client.force_login(verified_user)

    old_email = verified_user.email

    client.post(
        reverse("account_email"),
        email_change_data,
    )

    verified_user.refresh_from_db()

    assert verified_user.email == old_email


@pytest.mark.django_db
def test_user_can_confirm_email_change(
    client,
    email_change_confirmation_url,
    verified_user,
    email_change_data,
):
    client.force_login(verified_user)

    response = client.post(email_change_confirmation_url)

    assert response.status_code == 302

    verified_user.refresh_from_db()

    assert verified_user.email == email_change_data["email"]


@pytest.mark.django_db
def test_email_change_updates_primary_email(
    client,
    verified_user,
    email_change_confirmation_url,
    email_change_data,
):
    client.force_login(verified_user)

    response = client.post(
        email_change_confirmation_url,
    )

    assert response.status_code == 302

    email = EmailAddress.objects.get(user=verified_user)

    assert email.email == email_change_data["email"]
    assert email.verified is True
    assert email.primary is True


@pytest.mark.django_db
def test_email_change_rejects_existing_email(
    client,
    verified_user,
    django_user_model,
):
    user = django_user_model.objects.create_user(
        email="test2@example.com",
        password="StrongPassword123!",
    )

    EmailAddress.objects.create(
        user=user,
        email=user.email,
        primary=True,
        verified=True,
    )

    client.force_login(verified_user)

    response = client.post(
        reverse("account_email"),
        {
            "email": user.email,
            "action_add": "Add",
        },
    )

    assert len(mail.outbox) == 0
    assert response.status_code == 200
    assert "email" in response.context["form"].errors
    assert not EmailAddress.objects.filter(
        user=verified_user,
        email=user.email,
    ).exists()


@pytest.mark.django_db
def test_email_change_rejects_invalid_email(
    client,
    verified_user,
    email_change_data,
):
    client.force_login(verified_user)

    data = email_change_data.copy()
    data["email"] = "wrong_email_format"

    response = client.post(
        reverse("account_email"),
        data,
    )

    assert response.status_code == 200
    assert len(mail.outbox) == 0
    assert "email" in response.context["form"].errors


@pytest.mark.django_db
def test_email_change_confirmation_link_cannot_be_reused(
    client,
    verified_user,
    email_change_confirmation_url,
    email_change_data,
):
    client.force_login(verified_user)

    response = client.post(email_change_confirmation_url)

    assert response.status_code == 302

    verified_user.refresh_from_db()
    assert verified_user.email == email_change_data["email"]

    response = client.post(email_change_confirmation_url)

    assert response.status_code == 404

    verified_user.refresh_from_db()
    assert verified_user.email == email_change_data["email"]

    assert EmailAddress.objects.filter(
        user=verified_user,
        email=email_change_data["email"],
        verified=True,
        primary=True,
    ).exists()
