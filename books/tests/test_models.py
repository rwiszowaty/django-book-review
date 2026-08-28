from datetime import date

import pytest

from django.db import IntegrityError
from django.core.exceptions import ValidationError

from books.models import Author, Book, Genre, Review


@pytest.mark.django_db
class TestAuthor:
    def test_create_author(self):
        author = Author.objects.create(
            first_name="Robert",
            last_name="Jordan",
        )

        assert author.pk is not None
        assert author.first_name == "Robert"
        assert author.last_name == "Jordan"

    def test_str(self, author):
        assert str(author) == "Robert Jordan"

    def test_author_ordering(self, author, second_author):
        authors = list(Author.objects.all())

        assert authors[0].last_name == "Jordan"
        assert authors[1].last_name == "Sanderson"


@pytest.mark.django_db
class TestGenre:
    def test_create_genre(self):
        genre = Genre.objects.create(
            name="Fantasy",
            slug="fantasy",
        )

        assert genre.name == "Fantasy"
        assert genre.slug == "fantasy"

    def test_str(self, genre):
        assert str(genre) == "Fantasy"

    def test_genre_name_is_unique(self, genre):
        with pytest.raises(IntegrityError):
            Genre.objects.create(
                name="Fantasy",
                slug="fantasy-2",
            )

    def test_genre_slug_is_unique(self, genre):
        with pytest.raises(IntegrityError):
            Genre.objects.create(
                name="Dark Fantasy",
                slug="fantasy",
            )


@pytest.mark.django_db
class TestBook:
    def test_create_book(self):
        book = Book.objects.create(
            title="The great hunt",
            slug="the great hunt",
            description="Short description.",
            isbn="1234567890123",
            publication_date=date(1985, 5, 1),
            pages=500,
        )

        assert book.title == "The great hunt"
        assert book.slug == "the great hunt"
        assert book.description == "Short description."
        assert book.isbn == "1234567890123"
        assert book.publication_date == date(1985, 5, 1)
        assert book.pages == 500

    def test_str(self, book):
        assert str(book) == "The great hunt"

    def test_can_have_multiple_authors(
        self,
        book,
        author,
        second_author,
    ):
        book.authors.add(author, second_author)

        assert book.authors.count() == 2
        assert author in book.authors.all()
        assert second_author in book.authors.all()

    def test_can_have_multiple_genres(
        self,
        book,
        genre,
    ):
        second_genre = Genre.objects.create(
            name="Sci-fi",
            slug="sci-fi",
        )

        book.genres.add(genre, second_genre)

        assert book.genres.count() == 2
        assert genre in book.genres.all()
        assert second_genre in book.genres.all()

    def test_slug_is_unique(self, book):
        with pytest.raises(IntegrityError):
            Book.objects.create(
                title="The eye of the world",
                slug=book.slug,
                isbn="0987654321123",
            )

    def test_isbn_is_unique(self, book):
        with pytest.raises(IntegrityError):
            Book.objects.create(
                title="The eye of the world",
                slug="the-eye-of-the-world",
                isbn=book.isbn,
            )

    def test_isbn_is_normalized(self):
        book = Book.objects.create(
            title="The Eye of the World",
            slug="the-eye-of-the-world",
            isbn="978-83-1234-56-7",
        )

        assert book.isbn == "978831234567"

    def test_book_ordering(self, book):
        Book.objects.create(
            title="The eye of the world",
            slug="the-eye-of-the-world",
            isbn="0987654321123",
        )

        books = list(Book.objects.all())

        assert books[0].title == "The eye of the world"
        assert books[1].title == "The great hunt"

    def test_cover_is_optional(self, book):
        assert not book.cover

    def test_add_cover(self, book, image_file, media_root):
        book.cover = image_file
        book.save()

        book.refresh_from_db()

        assert book.cover
        assert book.cover.name.startswith("book_covers/")
        assert book.cover.name.endswith(".jpg")
        assert book.cover.storage.exists(book.cover.name)


@pytest.mark.django_db
class TestReview:
    def test_create_review(self, book, user):
        review = Review.objects.create(
            book=book,
            user=user,
            content="Example of review.",
            rating=5,
        )

        assert review.book == book
        assert review.user == user
        assert review.content == "Example of review."
        assert review.rating == 5
        assert review.created_at is not None
        assert review.updated_at is not None

    def test_review_str(self, book, user):
        review = Review.objects.create(
            book=book,
            user=user,
            content="Example of review.",
            rating=5,
        )

        assert str(review) == f"{user} - {book}"

    def test_user_review_book_only_once(self, book, user):
        Review.objects.create(
            book=book,
            user=user,
            content="First review.",
            rating=5,
        )

        with pytest.raises(IntegrityError):
            Review.objects.create(
                book=book,
                user=user,
                content="Second review.",
                rating=1,
            )

    def test_review_rating_canont_be_less_than_one(self, book, user):
        review = Review(
            book=book,
            user=user,
            content="Example of review.",
            rating=0,
        )

        with pytest.raises(ValidationError):
            review.full_clean()

    def test_review_rating_canont_be_greater_than_one(self, book, user):
        review = Review(
            book=book,
            user=user,
            content="Example of review.",
            rating=6,
        )

        with pytest.raises(ValidationError):
            review.full_clean()
