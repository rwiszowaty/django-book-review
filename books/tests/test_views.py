from datetime import date

import pytest

from django.urls import reverse

from books.models import Book, Genre


@pytest.mark.django_db
class TestBookListView:
    def test_book_list_page_loads(self, client):
        response = client.get(
            reverse("books:book_list"),
        )

        assert response.status_code == 200

    def test_book_list_uses_correct_template(self, client):
        response = client.get(
            reverse("books:book_list"),
        )

        assert "book_list.html" in response.template_name

    def test_book_list_contains_book(self, client, book):
        response = client.get(
            reverse("books:book_list"),
        )

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

    def test_book_list_searches_by_title(self, client, book):
        response = client.get(
            reverse("books:book_list"),
            {"q": "great"},
        )

        assert response.status_code == 200
        assert list(response.context["books"]) == [book]

    def test_book_list_searches_by_author(self, client, book, author):
        book.authors.add(author)

        response = client.get(
            reverse("books:book_list"),
            {"q": "Jordan"},
        )

        assert response.status_code == 200
        assert list(response.context["books"]) == [book]

    def test_book_list_search_returns_no_results(self, client, book):
        response = client.get(
            reverse("books:book_list"),
            {"q": "nonexistent"},
        )

        assert response.status_code == 200
        assert list(response.context["books"]) == []

    def test_book_list_filters_by_author(self, client, book, author):
        book.authors.add(author)

        response = client.get(
            reverse("books:book_list"),
            {"author": author.id},
        )

        assert response.status_code == 200
        assert book in response.context["books"]

    def test_book_list_does_not_return_books_from_other_author(
        self,
        client,
        book,
        author,
        second_author,
    ):
        second_book = Book.objects.create(
            title="The Eye of the World",
            slug="the-eye-of-the-world",
            isbn="0987654321123",
        )

        book.authors.add(author)
        second_book.authors.add(second_author)

        response = client.get(
            reverse("books:book_list"),
            {"author": author.id},
        )

        assert book in response.context["books"]
        assert second_book not in response.context["books"]

    def test_book_list_filters_by_genre(self, client, book, genre):
        book.genres.add(genre)

        response = client.get(
            reverse("books:book_list"),
            {"genre": genre.slug},
        )

        assert response.status_code == 200
        assert book in response.context["books"]

    def test_book_list_does_not_return_books_from_other_genre(
        self,
        client,
        book,
        genre,
    ):
        second_book = Book.objects.create(
            title="The Eye of the World",
            slug="the-eye-of-the-world",
            isbn="0987654321123",
        )

        other_genre = Genre.objects.create(
            name="Sci-fi",
            slug="sci-fi",
        )

        book.genres.add(genre)
        second_book.genres.add(other_genre)

        response = client.get(
            reverse("books:book_list"),
            {"genre": genre.slug},
        )

        assert book in response.context["books"]
        assert second_book not in response.context["books"]

    def test_book_list_combines_search_and_genre(
        self,
        client,
        book,
        genre,
    ):
        book.genres.add(genre)

        response = client.get(
            reverse("books:book_list"),
            {
                "q": "great",
                "genre": genre.slug,
            },
        )

        assert list(response.context["books"]) == [book]

    def test_book_list_is_paginated(self, client, books):
        response = client.get(
            reverse("books:book_list"),
        )

        assert response.status_code == 200
        assert response.context["is_paginated"] is True
        assert response.context["paginator"].per_page == 10
        assert len(response.context["page_obj"]) == 10

    def test_book_list_page_two(self, client, books):
        response = client.get(
            reverse("books:book_list"),
            {"page": 2},
        )

        assert response.status_code == 200
        assert response.context["page_obj"].number == 2
        assert response.context["page_obj"].has_previous()
        assert not response.context["page_obj"].has_next()

    def test_book_list_does_not_duplicate_books(
        self,
        client,
        book,
        author,
        second_author,
    ):
        book.authors.add(author, second_author)

        response = client.get(
            reverse("books:book_list"),
            {"q": "Robert"},
        )

        books = list(response.context["books"])

        assert books.count(book) == 1

    def test_book_list_template(self, client, book, author, genre):
        book.authors.add(author)
        book.genres.add(genre)

        response = client.get(reverse("books:book_list"))

        assert book.title.encode() in response.content
        assert author.first_name.encode() in response.content
        assert author.last_name.encode() in response.content
        assert genre.name.encode() in response.content

    def test_book_list_template_contains_search_form(self, client):
        response = client.get(
            reverse("books:book_list"),
        )

        assert b'name="q"' in response.content
        assert b'name="author"' in response.content
        assert b'name="genre"' in response.content

    def test_book_list_template_shows_no_result_message(self, client):
        response = client.get(
            reverse("books:book_list"),
        )

        assert "Nie znaleziono książek.".encode() in response.content


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

    def test_book_detail_returns_404_for_nonexistent_book(self, client):
        response = client.get(
            reverse(
                "books:book_detail",
                kwargs={"slug": "nonexistent_book"},
            )
        )

        assert response.status_code == 404

    def test_book_detail_template(
        self,
        client,
        book,
        author,
        genre,
        image_file,
        media_root,
    ):
        book.authors.add(author)
        book.genres.add(genre)
        book.description = "Short description."
        book.pages = 500
        book.publication_date = date(1985, 1, 1)
        book.cover = image_file

        book.save()

        response = client.get(
            reverse(
                "books:book_detail",
                kwargs={"slug": book.slug},
            )
        )

        assert book.title.encode() in response.content
        assert author.first_name.encode() in response.content
        assert author.last_name.encode() in response.content
        assert genre.name.encode() in response.content
        assert book.description.encode() in response.content
        assert book.isbn.encode() in response.content
        assert b"Liczba stron:" in response.content
        assert b"500" in response.content
        assert b"01.01.1985" in response.content
        assert book.cover.url.encode() in response.content
        assert f"Okładka książki {book.title}".encode() in response.content

    def test_book_detail_template_without_cover(self, client, book):
        response = client.get(
            reverse(
                "books:book_detail",
                kwargs={"slug": book.slug},
            )
        )

        assert response.status_code == 200
        assert b"<img" not in response.content
        assert "Brak okładki".encode() in response.content

    def test_book_detail_template_contains_back_link(self, client, book):
        response = client.get(
            reverse(
                "books:book_detail",
                kwargs={"slug": book.slug},
            )
        )

        assert "Powrót do książek".encode() in response.content
        assert reverse("books:book_list").encode() in response.content

    def test_book_detail_template_without_description(self, client, book):
        response = client.get(
            reverse(
                "books:book_detail",
                kwargs={"slug": book.slug},
            )
        )

        assert response.status_code == 200
        assert b"Opis" not in response.content
