import pytest

from allauth.account.models import EmailAddress

from users.forms import CustomAddEmailForm, UsernameForm


@pytest.mark.django_db
class TestCustomAddEmailForm:
    def test_add_email_form_rejects_existing_email(
        self,
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

    def test_add_email_form_accepts_new_email(
        self,
        verified_user,
    ):
        form = CustomAddEmailForm(
            data={"email": "new.email@example.com"},
            user=verified_user,
        )

        assert form.is_valid()
        assert form.cleaned_data["email"] == "new.email@example.com"

    def test_add_email_form_rejects_users_own_email(
        self,
        verified_user,
    ):
        form = CustomAddEmailForm(
            data={"email": verified_user.email},
            user=verified_user,
        )

        assert not form.is_valid()
        assert "email" in form.errors


@pytest.mark.django_db
class TestUsernameForm:
    def test_valid_username(self):
        form = UsernameForm(
            data={
                "username": "Nickname",
            }
        )

        assert form.is_valid()

    def test_username_is_required(self):
        form = UsernameForm(
            data={
                "username": "",
            }
        )

        assert not form.is_valid()
        assert "username" in form.errors

    def test_username_must_be_unique(self, registered_user):
        registered_user.username = "Nickname"
        registered_user.save()

        form = UsernameForm(
            data={
                "username": "Nickname",
            },
        )

        assert not form.is_valid()
        assert "username" in form.errors

    def test_form_saves_username(self, registered_user):
        user = registered_user

        form = UsernameForm(
            data={
                "username": "Nickname",
            },
            instance=user,
        )

        assert form.is_valid()

        updated_user = form.save()

        assert updated_user.username == "Nickname"
