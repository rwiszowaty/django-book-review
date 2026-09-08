from django.urls import path

from books.api.views import (
    BookDetailApiView,
    BookListApiView,
    BookReviewListApiView,
)

urlpatterns = [
    path(
        "books/",
        BookListApiView.as_view(),
        name="api_book_list",
    ),
    path(
        "books/<slug:slug>/",
        BookDetailApiView.as_view(),
        name="api_book_detail",
    ),
    path(
        "book/<slug:slug>/reviews/",
        BookReviewListApiView.as_view(),
        name="api_book_reviews",
    ),
]
