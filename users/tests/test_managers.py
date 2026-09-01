import pytest


@pytest.mark.django_db
class TestCustomUserManager:
    def test_create_user(self, django_user_model):

        user = django_user_model.objects.create_user(
            email="user@example.com",
            password="testpass123",
        )

        assert user.email == "user@example.com"
        assert user.check_password("testpass123")
        assert user.is_active is True
        assert user.is_staff is False
        assert user.is_superuser is False

    def test_create_user_without_email(self, django_user_model):

        with pytest.raises(ValueError, match="email"):
            django_user_model.objects.create_user(
                email="",
                password="testpass123",
            )

    def test_create_user_normalizes_email(self, django_user_model):

        user = django_user_model.objects.create_user(
            email="user@EXAMPLE.COM",
            password="testpass123",
        )

        assert user.email == "user@example.com"

    def test_create_superuser(self, django_user_model):

        user = django_user_model.objects.create_superuser(
            email="admin@example.com",
            password="testpass123",
        )

        assert user.email == "admin@example.com"
        assert user.check_password("testpass123")
        assert user.is_active is True
        assert user.is_staff is True
        assert user.is_superuser is True

    def test_create_superuser_requires_is_staff(self, django_user_model):

        with pytest.raises(
            ValueError,
            match="is_staff=True",
        ):
            django_user_model.objects.create_superuser(
                email="admin@example.com",
                password="testpass123",
                is_staff=False,
            )

    def test_create_superuser_requires_is_superuser(self, django_user_model):

        with pytest.raises(
            ValueError,
            match="is_superuser=True",
        ):
            django_user_model.objects.create_superuser(
                email="admin@example.com",
                password="testpass123",
                is_superuser=False,
            )

    def test_create_superuser_without_email(self, django_user_model):

        with pytest.raises(
            ValueError,
            match="email",
        ):
            django_user_model.objects.create_superuser(
                email="",
                password="testpass123",
            )
