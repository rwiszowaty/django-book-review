import pytest

from django.contrib import admin

from books.admin import AuthorAdmin, BookAdmin, GenreAdmin
from books.models import Author, Book, Genre


@pytest.mark.django_db
def test_author_admin_registered():
    assert isinstance(admin.site._registry[Author], AuthorAdmin)


@pytest.mark.django_db
def test_book_admin_registered():
    assert isinstance(admin.site._registry[Book], BookAdmin)


@pytest.mark.django_db
def test_genre_admin_registered():
    assert isinstance(admin.site._registry[Genre], GenreAdmin)


@pytest.mark.django_db
def test_author_admin_list_display():
    assert AuthorAdmin.list_display == ("first_name", "last_name")


@pytest.mark.django_db
def test_author_admin_search_fields():
    assert AuthorAdmin.search_fields == ("first_name", "last_name")


@pytest.mark.django_db
def test_genre_admin_list_display():
    assert GenreAdmin.list_display == ("name", "slug")


@pytest.mark.django_db
def test_genre_admin_search_fields():
    assert GenreAdmin.search_fields == ("name",)


@pytest.mark.django_db
def test_book_admin_list_display():
    assert BookAdmin.list_display == (
        "title",
        "isbn",
        "publication_date",
        "pages",
        "created_at",
    )


@pytest.mark.django_db
def test_book_admin_search_fields():
    assert BookAdmin.search_fields == (
        "title",
        "isbn",
        "authors__first_name",
        "authors__last_name",
    )


@pytest.mark.django_db
def test_book_admin_many_to_many_fields():
    assert BookAdmin.filter_horizontal == (
        "authors",
        "genres",
    )


@pytest.mark.django_db
def test_book_admin_readonly_fields():
    assert BookAdmin.readonly_fields == (
        "created_at",
        "updated_at",
    )
