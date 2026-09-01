import pytest


@pytest.mark.django_db
class TestCustomUser:
    def test_user_can_be_created_without_username(
        self,
        django_user_model,
    ):
        user = django_user_model.objects.create_user(
            email="user@example.com",
            password="testpass123",
        )

        assert user.username is None

    def test_email_is_username_field(self, django_user_model):
        assert django_user_model.USERNAME_FIELD == "email"

    def test_username_can_be_set(self, django_user_model):
        user = django_user_model.objects.create_user(
            email="user@example.com",
            password="testpass123",
        )

        user.username = "User displayed"
        user.save()

        assert user.username == "User displayed"
