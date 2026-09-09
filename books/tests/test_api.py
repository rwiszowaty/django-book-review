import pytest
from django.urls import reverse
from rest_framework import status

from books.models import Book, Review


@pytest.mark.django_db
class TestBookListApiView:
    def test_book_list_returns_200(
        self,
        client,
    ):
        response = client.get(
            reverse("api_book_list"),
        )

        assert response.status_code == status.HTTP_200_OK

    def test_book_list_returns_books(
        self,
        client,
        book,
    ):
        response = client.get(
            reverse("api_book_list"),
        )

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["id"] == book.id
        assert response.data[0]["title"] == book.title
        assert response.data[0]["slug"] == book.slug

    def test_book_list_returns_extended_book_data(
        self,
        client,
        book,
        author,
        genre,
        review,
    ):
        book.authors.add(author)
        book.genres.add(genre)

        response = client.get(
            reverse(
                "api_book_list",
            )
        )

        assert response.status_code == status.HTTP_200_OK

        data = response.data[0]

        assert data["authors"] == [str(author)]
        assert data["genres"] == [str(genre)]
        assert data["average_rating"] == 5.00

    def test_book_list_return_null_average_rating_without_reviews(
        self,
        client,
        book,
    ):
        response = client.get(
            reverse(
                "api_book_list",
            )
        )

        assert response.status_code == status.HTTP_200_OK

        data = response.data[0]

        assert data["average_rating"] is None


@pytest.mark.django_db
class TestBookDetailApiView:
    def test_book_detail_return_book(
        self,
        client,
        book,
    ):
        response = client.get(
            reverse(
                "api_book_detail",
                kwargs={"slug": book.slug},
            )
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == book.id
        assert response.data["title"] == book.title
        assert response.data["slug"] == book.slug

    def test_book_detail_returns_404_for_invalid_slug(
        self,
        client,
    ):
        response = client.get(
            reverse(
                "api_book_detail",
                kwargs={"slug": "non-existent-book"},
            )
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestBookReviewListCreateApi:
    def test_book_reviews_returns_reviews(
        self,
        client,
        book,
        review,
    ):
        response = client.get(
            reverse(
                "api_book_reviews",
                kwargs={"slug": book.slug},
            )
        )

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

        data = response.data[0]

        assert data["id"] == review.id
        assert data["user"] == str(review.user)
        assert data["content"] == review.content
        assert data["rating"] == review.rating

    def test_book_reviews_returns_empty_list_without_reviews(
        self,
        client,
        book,
    ):
        response = client.get(
            reverse(
                "api_book_reviews",
                kwargs={"slug": book.slug},
            )
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data == []

    def test_book_reviews_return_only_reviews_for_selected_book(
        self,
        client,
        book,
        review,
        user_with_username,
    ):
        other_book = Book.objects.create(
            title="Other book",
            slug="other-book",
            isbn="123456790321",
        )

        other_review = Review.objects.create(
            book=other_book,
            user=user_with_username,
            content="Other review.",
            rating=3,
        )

        response = client.get(
            reverse(
                "api_book_reviews",
                kwargs={"slug": book.slug},
            )
        )

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

        data = response.data[0]

        assert data["id"] == review.id
        assert data["id"] != other_review.id

    def test_authenticated_user_with_username_can_create_review(
        self,
        client,
        book,
        user_with_username,
    ):
        client.force_login(user_with_username)

        response = client.post(
            reverse(
                "api_book_reviews",
                kwargs={"slug": book.slug},
            ),
            data={
                "content": "Book review.",
                "rating": 5,
            },
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["content"] == "Book review."
        assert response.data["rating"] == 5
        assert response.data["user"] == str(user_with_username)

        review = Review.objects.get(
            book=book,
            user=user_with_username,
        )

        assert review.content == "Book review."
        assert review.rating == 5

    def test_authenticated_user_without_username_cannot_create_review(
        self,
        client,
        book,
        user,
    ):
        client.force_login(user)

        response = client.post(
            reverse(
                "api_book_reviews",
                kwargs={"slug": book.slug},
            ),
            data={
                "content": "Book review.",
                "rating": 5,
            },
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert not Review.objects.filter(
            book=book,
            user=user,
        ).exists()

    def test_anonymous_user_cannot_create_review(
        self,
        client,
        book,
    ):
        response = client.post(
            reverse(
                "api_book_reviews",
                kwargs={"slug": book.slug},
            ),
            data={
                "content": "Book review.",
                "rating": 5,
            },
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert not Review.objects.filter(
            book=book,
        ).exists()

    @pytest.mark.parametrize("rating", [0, 6])
    def test_user_cannot_create_review_with_invalid_rating(
        self,
        client,
        book,
        user_with_username,
        rating,
    ):
        client.force_login(user_with_username)

        response = client.post(
            reverse(
                "api_book_reviews",
                kwargs={"slug": book.slug},
            ),
            data={
                "content": "Book review.",
                "rating": rating,
            },
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "rating" in response.data
        assert not Review.objects.filter(
            book=book,
            user=user_with_username,
        ).exists()

    def test_user_cannot_create_review_with_empty_content(
        self,
        client,
        book,
        user_with_username,
    ):
        client.force_login(user_with_username)

        response = client.post(
            reverse(
                "api_book_reviews",
                kwargs={"slug": book.slug},
            ),
            data={
                "content": "",
                "rating": 5,
            },
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "content" in response.data
        assert not Review.objects.filter(
            book=book,
            user=user_with_username,
        ).exists()

    def test_user_cannot_create_second_review_for_same_book(
        self,
        client,
        book,
        user_with_username,
        review,
    ):
        client.force_login(user_with_username)

        response = client.post(
            reverse(
                "api_book_reviews",
                kwargs={"slug": book.slug},
            ),
            data={
                "content": "Another review.",
                "rating": 4,
            },
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Użytkownik może dodać tylko jedną recenzję do książki." in str(
            response.data
        )
        assert (
            Review.objects.filter(
                book=book,
                user=user_with_username,
            ).count()
            == 1
        )

    def test_cannot_create_review_for_nonexistent_book(
        self,
        client,
        user_with_username,
    ):
        client.force_login(user_with_username)

        response = client.post(
            reverse(
                "api_book_reviews",
                kwargs={"slug": "non-existent-book"},
            ),
            data={
                "content": "Example review.",
                "rating": 5,
            },
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_review_endpoint_does_not_allow_update(
        self,
        client,
        book,
        user_with_username,
        review,
    ):
        client.force_login(user_with_username)

        response = client.put(
            reverse(
                "api_book_reviews",
                kwargs={"slug": book.slug},
            ),
            data={
                "content": "Updated review.",
                "rating": 4,
            },
        )

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_review_endpoint_does_not_allow_delete(
        self,
        client,
        book,
        user_with_username,
        review,
    ):
        client.force_login(user_with_username)

        response = client.delete(
            reverse(
                "api_book_reviews",
                kwargs={"slug": book.slug},
            ),
        )

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
