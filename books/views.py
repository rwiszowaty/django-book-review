from django.db.models import Q
from django.views.generic import ListView, DetailView

from .models import Author, Book, Genre


class BookListView(ListView):
    model = Book
    template_name = "book_list.html"
    context_object_name = "books"
    paginate_by = 10

    def get_queryset(self):
        queryset = Book.objects.prefetch_related("authors", "genres").all()

        query = self.request.GET.get("q")
        genre = self.request.GET.get("genre")
        author = self.request.GET.get("author")

        if query:
            queryset = queryset.filter(
                Q(title__icontains=query)
                | Q(authors__first_name__icontains=query)
                | Q(authors__last_name__icontains=query)
            )

        if genre:
            queryset = queryset.filter(genres__slug=genre)

        if author:
            queryset = queryset.filter(authors__id=author)

        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["genres"] = Genre.objects.all()
        context["authors"] = Author.objects.all()

        return context


class BookDetailView(DetailView):
    model = Book
    template_name = "book_detail.html"
    context_object_name = "book"
    slug_field = "slug"
    slug_url_kwarg = "slug"
