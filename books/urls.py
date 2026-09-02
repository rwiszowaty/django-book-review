from django.urls import path

from .views import BookDetailView, BookListView, ReviewUpdateView

app_name = "books"

urlpatterns = [
    path("", BookListView.as_view(), name="book_list"),
    path("books/<slug:slug>/", BookDetailView.as_view(), name="book_detail"),
    path("reviews/<int:pk>/edit/", ReviewUpdateView.as_view(), name="review_edit"),
]
