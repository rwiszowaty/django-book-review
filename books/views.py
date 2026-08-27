from django.views.generic import ListView, DetailView

from .models import Book


class BookListView(ListView):
    model = Book
    template_name = "book_list.html"
    context_object_name = "books"


class BookDetailView(DetailView):
    model = Book
    template_name = "book_detail.html"
    context_object_name = "book"
    slug_field = "slug"
    slug_url_kwarg = "slug"
