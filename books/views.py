from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import DetailView, ListView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import ReviewForm
from .models import Author, Book, Genre, Review


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

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        if not request.user.is_authenticated:
            return redirect("account_login")

        if not request.user.username:
            return redirect("users:set_username")

        if Review.objects.filter(
            book=self.object,
            user=request.user,
        ).exists():
            return redirect(
                "books:book_detail",
                slug=self.object.slug,
            )

        form = ReviewForm(request.POST)

        if form.is_valid():
            review = form.save(commit=False)
            review.book = self.object
            review.user = request.user
            review.save()

            return redirect(
                "books:book_detail",
                slug=self.object.slug,
            )

        return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if "form" not in context:
            context["form"] = ReviewForm()

        if self.request.user.is_authenticated:
            context["user_review"] = Review.objects.filter(
                book=self.object,
                user=self.request.user,
            ).first()
        else:
            context["user_review"] = None

        return context


class ReviewUpdateView(LoginRequiredMixin, UpdateView):
    model = Review
    form_class = ReviewForm
    template_name = "review_edit.html"
    context_object_name = "review"

    def get_queryset(self):
        return Review.objects.filter(
            user=self.request.user,
        )

    def get_success_url(self):
        return reverse(
            "books:book_detail",
            kwargs={"slug": self.object.book.slug},
        )
