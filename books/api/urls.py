from django.urls import path

from books.api.views import (
    BookDetailApiView,
    BookListApiView,
    BookReviewListCreateApiView,
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
        "books/<slug:slug>/reviews/",
        BookReviewListCreateApiView.as_view(),
        name="api_book_reviews",
    ),
]
