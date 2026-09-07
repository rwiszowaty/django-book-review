import pytest
from django.urls import reverse

from books.models import Review
from users.forms import UsernameForm


@pytest.mark.django_db
class TestSetUsernameView:
    def test_authenticated_user_can_access_view(
        self,
        client,
        registered_user,
    ):
        client.force_login(registered_user)

        response = client.get(
            reverse("users:set_username"),
        )

        assert response.status_code == 200
        assert isinstance(
            response.context["form"],
            UsernameForm,
        )

    def test_anonymous_user_cannot_access_view(
        self,
        client,
    ):
        response = client.get(
            reverse("users:set_username"),
        )

        assert response.status_code == 302
        assert "accounts/login/" in response.url

    def test_user_can_set_username(
        self,
        client,
        registered_user,
        django_user_model,
    ):
        client.force_login(registered_user)

        response = client.post(
            reverse("users:set_username"),
            {
                "username": "Nickname",
            },
        )

        assert response.status_code == 302
        assert response.url == reverse("books:book_list")

        registered_user.refresh_from_db()

        assert registered_user.username == "Nickname"


@pytest.mark.django_db
class TestProfileView:
    def test_authenticated_user_can_access_profile(
        self,
        client,
        user_with_username,
    ):
        client.force_login(user_with_username)

        response = client.get(
            reverse("users:profile"),
        )

        assert response.status_code == 200

    def test_anonymous_user_is_redirected_to_login(
        self,
        client,
    ):
        response = client.get(
            reverse("users:profile"),
        )

        assert response.status_code == 302
        assert "/accounts/login/" in response.url

    def test_profile_contains_users_data(
        self,
        client,
        review,
        user_with_username,
    ):
        client.force_login(user_with_username)

        response = client.get(
            reverse("users:profile"),
        )

        content = response.content.decode()

        assert user_with_username.username in content
        assert user_with_username.email in content
        assert (
            response.context["profile_user"].date_joined
            == user_with_username.date_joined
        )
        assert response.context["review_count"] == 1

    def test_profile_contains_user_reviews(
        self,
        client,
        review,
        user_with_username,
    ):
        client.force_login(user_with_username)

        response = client.get(
            reverse(
                "users:profile",
            )
        )

        assert review.content in response.content.decode()

    def test_profile_does_not_contain_other_users_reviews(
        self,
        client,
        book,
        review,
        django_user_model,
    ):
        second_user = django_user_model.objects.create_user(
            email="second@example.com",
            password="StrongPassword123!",
            username="Second Reader",
        )

        other_review = Review.objects.create(
            book=book,
            user=second_user,
            content="Review by second user.",
            rating=5,
        )

        client.force_login(second_user)

        response = client.get(
            reverse(
                "users:profile",
            )
        )

        content = response.content.decode()

        assert review.content not in content
        assert other_review.content in content

    def test_profile_for_user_without_reviews(
        self,
        client,
        user_with_username,
    ):
        client.force_login(user_with_username)

        response = client.get(
            reverse(
                "users:profile",
            )
        )

        content = response.content.decode()

        assert "Moje recenzje" in content
        assert "Nie masz jeszcze żadnych recenzji." in content


class TestProfileEditView:
    def test_authenticated_user_can_access_profile_edit(
        self,
        client,
        user_with_username,
    ):
        client.force_login(user_with_username)

        response = client.get(
            reverse("users:profile_edit"),
        )

        assert response.status_code == 200

    def test_anonymous_user_is_redirect_to_login(
        self,
        client,
    ):
        response = client.get(
            reverse("users:profile_edit"),
        )

        assert response.status_code == 302
        assert "/accounts/login/" in response.url

    def test_user_can_change_username(
        self,
        client,
        user_with_username,
    ):
        client.force_login(user_with_username)

        response = client.post(
            reverse("users:profile_edit"),
            {
                "username": "NewNickname",
            },
        )

        assert response.status_code == 302
        assert response.url == reverse("users:profile")

        user_with_username.refresh_from_db()

        assert user_with_username.username == "NewNickname"

    def test_profile_contains_edit_profile_link(
        self,
        client,
        user_with_username,
    ):
        client.force_login(user_with_username)

        response = client.get(
            reverse("users:profile"),
        )

        assert reverse("users:profile_edit") in response.content.decode()

    def test_user_cannot_change_username_to_existing_username(
        self,
        client,
        user_with_username,
        django_user_model,
    ):
        second_user = django_user_model.objects.create(
            email="seconduser@example.com",
            password="StrongPassword123!",
            username="Second User",
        )

        client.force_login(user_with_username)

        response = client.post(
            reverse("users:profile_edit"),
            {
                "username": "Second User",
            },
        )

        assert response.status_code == 200
        assert "username" in response.context["form"].errors

        user_with_username.refresh_from_db()

        assert user_with_username.username != second_user.username

    def test_user_cannot_set_empty_username(
        self,
        client,
        user_with_username,
    ):
        client.force_login(user_with_username)

        response = client.post(
            reverse("users:profile_edit"),
            {
                "username": "",
            },
        )

        assert response.status_code == 200
        assert "username" in response.context["form"].errors

        user_with_username.refresh_from_db()

        assert user_with_username.username


@pytest.mark.django_db
class TestPublicProfileView:
    def test_user_can_access_public_profile(
        self,
        client,
        user_with_username,
        second_user,
    ):
        client.force_login(user_with_username)

        response = client.get(
            reverse(
                "users:public_profile",
                kwargs={
                    "username": second_user.username,
                },
            )
        )

        assert response.status_code == 200

    def test_anonymous_user_can_access_public_profile(
        self,
        client,
        user_with_username,
    ):
        response = client.get(
            reverse(
                "users:public_profile",
                kwargs={
                    "username": user_with_username.username,
                },
            )
        )

        assert response.status_code == 200

    def test_public_profile_contains_user_data(
        self,
        client,
        user_with_username,
        review,
    ):
        response = client.get(
            reverse(
                "users:public_profile",
                kwargs={
                    "username": user_with_username.username,
                },
            )
        )

        content = response.content.decode()

        assert user_with_username.username in content
        assert user_with_username.email not in content
        assert review.content in content
        assert response.context["review_count"] == 1

    def test_public_profile_does_not_contain_other_users_reviews(
        self,
        client,
        book,
        user_with_username,
        review,
        second_user,
    ):
        other_review = Review.objects.create(
            book=book,
            user=second_user,
            content="Second review.",
            rating=5,
        )

        response = client.get(
            reverse(
                "users:public_profile",
                kwargs={
                    "username": user_with_username.username,
                },
            )
        )

        content = response.content.decode()

        assert review.content in content
        assert other_review.content not in content

    def test_public_profile_contains_rating_stars(
        self,
        client,
        user_with_username,
        review,
    ):
        response = client.get(
            reverse(
                "users:public_profile",
                kwargs={
                    "username": user_with_username.username,
                },
            )
        )

        assert "bi-star-fill" in response.content.decode()

    def test_public_profile_for_user_without_reviews(
        self,
        client,
        user_with_username,
    ):
        response = client.get(
            reverse(
                "users:public_profile",
                kwargs={
                    "username": user_with_username.username,
                },
            )
        )

        content = response.content.decode()

        assert "Ten użytkownik nie ma jeszcze żadnych recenzji." in content

    def test_public_profile_returns_404_for_nonexistent_user(
        self,
        client,
    ):
        response = client.get(
            reverse(
                "users:public_profile",
                kwargs={"username": "nonexistent"},
            )
        )

        assert response.status_code == 404

    def test_public_profile_contains_link_to_books(
        self,
        client,
        user_with_username,
    ):
        response = client.get(
            reverse(
                "users:public_profile",
                kwargs={
                    "username": user_with_username.username,
                },
            ),
        )

        expected_url = reverse("books:book_list")

        assert expected_url in response.content.decode()
