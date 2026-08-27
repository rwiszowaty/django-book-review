import pytest

from django.urls import reverse

from books.models import Book


@pytest.mark.django_db
class TestBookListView:
    def test_book_list_page_loads(self, client):
        response = client.get(reverse("books:book_list"))

        assert response.status_code == 200

    def test_book_list_uses_correct_template(self, client):
        response = client.get(reverse("books:book_list"))

        assert "book_list.html" in response.template_name

    def test_book_list_contains_book(self, client, book):
        response = client.get(reverse("books:book_list"))

        assert book in response.context["books"]

    def test_book_list_contains_multiple_books(self, client, book):
        second_book = Book.objects.create(
            title="The Eye of the World",
            slug="the-eye-of-the-world",
            isbn="0987654321123",
        )

        response = client.get(reverse("books:book_list"))

        books = response.context["books"]

        assert book in books
        assert second_book in books
        assert len(books) == 2


@pytest.mark.django_db
class TestBookDetailView:
    def test_book_detail_page_loads(self, client, book):
        response = client.get(
            reverse(
                "books:book_detail",
                kwargs={"slug": book.slug},
            )
        )

        assert response.status_code == 200

    def test_book_detail_uses_correct_template(self, client, book):
        response = client.get(
            reverse(
                "books:book_detail",
                kwargs={"slug": book.slug},
            )
        )

        assert response.template_name == ["book_detail.html"]

    def test_book_detail_contains_book(self, client, book):
        response = client.get(
            reverse(
                "books:book_detail",
                kwargs={"slug": book.slug},
            )
        )

        assert response.context["book"] == book

    def test_book_detail_contains_book_title(self, client, book):
        response = client.get(
            reverse(
                "books:book_detail",
                kwargs={"slug": book.slug},
            )
        )

        assert book.title.encode() in response.content

    def test_book_detail_returns_404_for_nonexistent_book(self, client):
        response = client.get(
            reverse(
                "books:book_detail",
                kwargs={"slug": "nonexistent_book"},
            )
        )

        assert response.status_code == 404
