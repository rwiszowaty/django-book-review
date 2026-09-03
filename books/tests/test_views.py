from datetime import date

import pytest

from django.urls import reverse

from books.models import Book, Genre, Review


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

    def test_book_detail_contains_review(
        self,
        client,
        book,
        user_with_username,
    ):
        review = Review.objects.create(
            book=book,
            user=user_with_username,
            content="Example of book review.",
            rating=5,
        )

        response = client.get(
            reverse(
                "books:book_detail",
                kwargs={"slug": book.slug},
            )
        )

        assert review in response.context["book"].reviews.all()

    def test_book_detail_template_contains_review(
        self,
        client,
        book,
        user_with_username,
    ):
        Review.objects.create(
            book=book,
            user=user_with_username,
            content="Example of book review.",
            rating=5,
        )

        response = client.get(
            reverse(
                "books:book_detail",
                kwargs={"slug": book.slug},
            )
        )

        assert b"Example of book review." in response.content

    def test_book_detail_template_contains_review_username(
        self,
        client,
        book,
        user_with_username,
    ):
        Review.objects.create(
            book=book,
            user=user_with_username,
            content="Example of book review.",
            rating=5,
        )

        response = client.get(
            reverse(
                "books:book_detail",
                kwargs={"slug": book.slug},
            )
        )

        assert b"Nickname" in response.content
        assert b"test@example.com" not in response.content

    def test_book_detail_template_contains_reviews_rating(
        self,
        client,
        book,
        user_with_username,
    ):
        Review.objects.create(
            book=book,
            user=user_with_username,
            content="Example of book review.",
            rating=5,
        )

        response = client.get(
            reverse(
                "books:book_detail",
                kwargs={"slug": book.slug},
            )
        )

        assert b"5" in response.content

    def test_book_detail_contains_mulditple_reviews(
        self,
        client,
        book,
        user_with_username,
        django_user_model,
    ):
        second_user = django_user_model.objects.create_user(
            email="second@example.com",
            password="StrongPassword123!",
            username="Second Reader",
        )

        Review.objects.create(
            book=book,
            user=user_with_username,
            content="Example of book review.",
            rating=5,
        )

        Review.objects.create(
            book=book,
            user=second_user,
            content="Second book review.",
            rating=4,
        )

        response = client.get(
            reverse(
                "books:book_detail",
                kwargs={"slug": book.slug},
            )
        )

        assert b"Example of book review." in response.content
        assert b"Nickname" in response.content
        assert b"Second book review." in response.content
        assert b"Second Reader" in response.content

    def test_book_detail_context_contains_user_review(
        self,
        client,
        book,
        user_with_username,
    ):
        client.force_login(user_with_username)

        review = Review.objects.create(
            book=book,
            user=user_with_username,
            content="Example of book review.",
            rating=5,
        )

        response = client.get(
            reverse(
                "books:book_detail",
                kwargs={"slug": book.slug},
            )
        )

        assert response.context["user_review"] == review

    def test_book_detail_context_user_review_is_none_without_review(
        self,
        client,
        book,
        user_with_username,
    ):
        client.force_login(user_with_username)

        response = client.get(
            reverse(
                "books:book_detail",
                kwargs={"slug": book.slug},
            )
        )

        assert response.context["user_review"] is None

    def test_book_detail_context_user_review_is_none_for_anonymous(
        self,
        client,
        book,
    ):
        response = client.get(
            reverse(
                "books:book_detail",
                kwargs={"slug": book.slug},
            )
        )

        assert response.context["user_review"] is None

    def test_book_detail_template_shows_review_form_for_authenticated(
        self,
        client,
        book,
        user_with_username,
    ):
        client.force_login(user_with_username)

        response = client.get(
            reverse(
                "books:book_detail",
                kwargs={"slug": book.slug},
            )
        )

        assert b'name="content"' in response.content
        assert b'name="rating"' in response.content

    def test_book_detail_hides_review_form_after_user_review(
        self,
        client,
        book,
        user_with_username,
    ):
        client.force_login(user_with_username)

        Review.objects.create(
            book=book,
            user=user_with_username,
            content="Example of book review.",
            rating=5,
        )

        response = client.get(
            reverse(
                "books:book_detail",
                kwargs={"slug": book.slug},
            )
        )

        assert b'name="content"' not in response.content
        assert b'name="rating"' not in response.content
        assert "Dodałeś już recenzję".encode() in response.content

    def test_book_detail_shows_login_message_for_anonymous_user(
        self,
        client,
        book,
    ):
        response = client.get(
            reverse(
                "books:book_detail",
                kwargs={"slug": book.slug},
            )
        )

        assert "Zaloguj się, aby dodać recenzję.".encode() in response.content
        assert b'name="content"' not in response.content

    def test_book_detail_shows_averange_rating(
        self,
        client,
        book,
        review,
        second_user,
    ):
        Review.objects.create(
            book=book,
            user=second_user,
            content="Second review.",
            rating=1,
        )

        response = client.get(
            reverse(
                "books:book_detail",
                kwargs={"slug": book.slug},
            )
        )

        assert response.status_code == 200
        assert response.context["average_rating"] == 3

    def test_book_detail_without_reviews_has_no_average_rating(
        self,
        client,
        book,
    ):
        response = client.get(
            reverse(
                "books:book_detail",
                kwargs={"slug": book.slug},
            )
        )

        assert response.status_code == 200
        assert response.context["average_rating"] is None
        assert response.context["rating_stars"] == []
        assert response.context["review_count"] == 0

    def test_book_detail_displays_average_rating(
        self,
        client,
        book,
        review,
        second_user,
    ):
        Review.objects.create(
            book=book,
            user=second_user,
            content="Second review.",
            rating=2,
        )

        response = client.get(
            reverse(
                "books:book_detail",
                kwargs={"slug": book.slug},
            ),
        )

        assert b"3.50/5" in response.content

    def test_book_detail_rating_stars(
        self,
        client,
        book,
        review,
        second_user,
    ):
        Review.objects.create(
            book=book,
            user=second_user,
            content="Second review.",
            rating=2,
        )

        response = client.get(
            reverse(
                "books:book_detail",
                kwargs={"slug": book.slug},
            )
        )

        assert response.context["rating_stars"] == [
            "bi-star-fill",
            "bi-star-fill",
            "bi-star-fill",
            "bi-star-half",
            "bi-star",
        ]

    def test_book_detail_shows_review_count(
        self,
        client,
        book,
        review,
        second_user,
    ):
        Review.objects.create(
            book=book,
            user=second_user,
            content="Second review.",
            rating=2,
        )

        response = client.get(
            reverse(
                "books:book_detail",
                kwargs={"slug": book.slug},
            )
        )

        assert response.context["review_count"] == 2


@pytest.mark.django_db
class TestReviewView:
    def test_anonymous_user_cannot_add_review(self, client, book):
        response = client.post(
            reverse(
                "books:book_detail",
                kwargs={"slug": book.slug},
            ),
            {
                "content": "Example of book review.",
                "rating": 5,
            },
        )

        assert response.status_code == 302
        assert "/accounts/login/" in response.url

    def test_authenticated_user_can_add_review(
        self,
        client,
        book,
        user_with_username,
    ):
        client.force_login(user_with_username)

        response = client.post(
            reverse(
                "books:book_detail",
                kwargs={"slug": book.slug},
            ),
            {
                "content": "Example of book review.",
                "rating": 5,
            },
        )

        assert response.status_code == 302
        assert response.url == reverse(
            "books:book_detail",
            kwargs={"slug": book.slug},
        )

        review = Review.objects.get(
            book=book,
            user=user_with_username,
        )

        assert review.content == "Example of book review."
        assert review.rating == 5

    def test_user_cannot_add_second_review(
        self,
        client,
        book,
        user_with_username,
    ):
        client.force_login(user_with_username)

        Review.objects.create(
            book=book,
            user=user_with_username,
            content="Example of book review.",
            rating=5,
        )

        client.post(
            reverse(
                "books:book_detail",
                kwargs={"slug": book.slug},
            ),
            {
                "content": "Second review.",
                "rating": 4,
            },
        )

        assert (
            Review.objects.filter(
                book=book,
                user=user_with_username,
            ).count()
            == 1
        )

    @pytest.mark.parametrize("rating", [0, 6])
    def test_invalid_rating_does_not_create_review(
        self,
        client,
        book,
        user_with_username,
        rating,
    ):
        client.force_login(user_with_username)

        response = client.post(
            reverse(
                "books:book_detail",
                kwargs={"slug": book.slug},
            ),
            {
                "content": "Example of book review.",
                "rating": rating,
            },
        )

        assert response.status_code == 200
        assert not Review.objects.filter(
            book=book,
            user=user_with_username,
        ).exists()

    def test_user_without_username_cannot_add_review(
        self,
        client,
        book,
        user,
    ):
        client.force_login(user)

        response = client.post(
            reverse(
                "books:book_detail",
                kwargs={"slug": book.slug},
            ),
            {
                "content": "Example of book review.",
                "rating": 5,
            },
        )

        assert response.status_code == 302
        assert not Review.objects.filter(
            book=book,
            user=user,
        ).exists()


@pytest.mark.django_db
class TestReviewUpdateView:
    def test_user_can_access_edit_view(
        self,
        client,
        review,
        user_with_username,
    ):
        client.force_login(user_with_username)

        response = client.get(
            reverse(
                "books:review_edit",
                kwargs={"pk": review.pk},
            ),
        )

        assert response.status_code == 200

    def test_edit_view_contains_curret_review_data(
        self,
        client,
        review,
        user_with_username,
    ):
        client.force_login(user_with_username)

        response = client.get(
            reverse(
                "books:review_edit",
                kwargs={"pk": review.pk},
            ),
        )

        assert response.context["form"].initial["content"] == (
            "Example of book review."
        )
        assert response.context["form"].initial["rating"] == 5

    def test_user_can_update_own_review(
        self,
        client,
        review,
        user_with_username,
    ):
        client.force_login(user_with_username)

        response = client.post(
            reverse(
                "books:review_edit",
                kwargs={"pk": review.pk},
            ),
            {
                "content": "Updated review.",
                "rating": 3,
            },
        )

        assert response.status_code == 302

        review.refresh_from_db()

        assert review.content == "Updated review."
        assert review.rating == 3

    def test_user_cannot_update_anothers_user_review(
        self,
        client,
        review,
        django_user_model,
    ):
        second_user = django_user_model.objects.create(
            email="second_user@example.com",
            password="StrongPassword123!",
            username="Second User",
        )
        client.force_login(second_user)

        response = client.get(
            reverse(
                "books:review_edit",
                kwargs={"pk": review.pk},
            )
        )

        assert response.status_code == 404

    def test_anonymous_user_is_redirected_to_login(
        self,
        client,
        review,
        user_with_username,
    ):
        response = client.get(
            reverse(
                "books:review_edit",
                kwargs={"pk": review.pk},
            ),
        )

        assert response.status_code == 302
        assert "/accounts/login" in response.url

    def test_book_detail_shows_edit_button_for_own_review(
        self,
        client,
        book,
        review,
        user_with_username,
    ):
        client.force_login(user_with_username)

        response = client.get(
            reverse(
                "books:book_detail",
                kwargs={"slug": book.slug},
            ),
        )

        assert "Edytuj recenzję".encode() in response.content

    def test_book_detail_does_not_show_edit_button_for_anonymous(
        self,
        client,
        book,
        review,
    ):
        response = client.get(
            reverse(
                "books:book_detail",
                kwargs={"slug": book.slug},
            ),
        )

        assert not "Edytuj recenzję".encode() in response.content


@pytest.mark.django_db
class TestReviewDeleteView:
    def test_user_can_access_delete_view(
        self,
        client,
        review,
        user_with_username,
    ):
        client.force_login(user_with_username)

        response = client.get(
            reverse(
                "books:review_delete",
                kwargs={"pk": review.pk},
            ),
        )

        assert response.status_code == 200

    def test_user_can_delete_own_review(
        self,
        client,
        review,
        user_with_username,
    ):
        client.force_login(user_with_username)

        response = client.post(
            reverse(
                "books:review_delete",
                kwargs={"pk": review.pk},
            ),
        )

        assert response.status_code == 302
        assert not Review.objects.filter(pk=review.pk).exists()

    def test_user_cannot_delete_another_user_review(
        self,
        client,
        review,
        django_user_model,
    ):
        second_user = django_user_model.objects.create(
            email="second_user@example.com",
            password="StrongPassword123!",
            username="Second User",
        )

        client.force_login(second_user)

        response = client.post(
            reverse(
                "books:review_delete",
                kwargs={"pk": review.pk},
            )
        )

        assert response.status_code == 404

    def test_anonymous_user_is_redirected_to_login(
        self,
        client,
        review,
    ):
        response = client.get(
            reverse(
                "books:review_delete",
                kwargs={"pk": review.pk},
            )
        )

        assert response.status_code == 302
        assert "/accounts/login/" in response.url

    def test_book_detail_shows_delete_button_for_own_review(
        self,
        client,
        book,
        review,
        user_with_username,
    ):
        client.force_login(user_with_username)

        response = client.get(
            reverse(
                "books:book_detail",
                kwargs={"slug": book.slug},
            ),
        )

        assert "Usuń recenzję".encode() in response.content

    def test_book_detail_does_not_show_edit_delete_for_anonymous(
        self,
        client,
        book,
        review,
    ):
        response = client.get(
            reverse(
                "books:book_detail",
                kwargs={"slug": book.slug},
            ),
        )

        assert not "Usuń recenzję".encode() in response.content
