import pytest
from django.urls import reverse
from rest_framework import status


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
