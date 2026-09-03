from decimal import Decimal, ROUND_HALF_UP

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg, F, Q
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import DeleteView, DetailView, ListView, UpdateView


from .forms import ReviewForm
from .models import Author, Book, Genre, Review


class BookListView(ListView):
    model = Book
    template_name = "book_list.html"
    context_object_name = "books"
    paginate_by = 10

    def get_queryset(self):
        queryset = Book.objects.prefetch_related(
            "authors",
            "genres",
        ).annotate(
            average_rating=Avg("reviews__rating"),
        )

        query = self.request.GET.get("q")
        genre = self.request.GET.get("genre")
        author = self.request.GET.get("author")
        sort = self.request.GET.get("sort")

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

        if sort == "rating":
            queryset = queryset.order_by(
                F("average_rating").desc(nulls_last=True),
                "title",
            )
        elif sort == "title":
            queryset = queryset.order_by("title")
        else:
            queryset = queryset.order_by("-id")

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

            messages.success(request, "Recenzja została dodana.")

            return redirect(
                "books:book_detail",
                slug=self.object.slug,
            )

        return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        average_rating = self.object.reviews.aggregate(average=Avg("rating"))["average"]

        context["average_rating"] = average_rating
        context["review_count"] = self.object.reviews.count()

        if average_rating is not None:
            rounded_rating = (Decimal(str(average_rating)) * 2).quantize(
                Decimal("1"),
                rounding=ROUND_HALF_UP,
            ) / 2

            full_stars = int(rounded_rating)
            half_star = rounded_rating % 1 == Decimal("0.5")
            empty_stars = 5 - full_stars - int(half_star)

            context["rating_stars"] = (
                ["bi-star-fill"] * full_stars
                + (["bi-star-half"] if half_star else [])
                + ["bi-star"] * empty_stars
            )
        else:
            context["rating_stars"] = []

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

    def form_valid(self, form):
        messages.success(
            self.request,
            "Recenzja została zaktualizowana.",
        )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            "books:book_detail",
            kwargs={"slug": self.object.book.slug},
        )


class ReviewDeleteView(LoginRequiredMixin, DeleteView):
    model = Review
    template_name = "review_delete.html"
    context_object_name = "review"

    def get_queryset(self):
        return Review.objects.filter(
            user=self.request.user,
        )

    def form_valid(self, form):
        messages.success(
            self.request,
            "Recenzja została usunięta.",
        )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            "books:book_detail",
            kwargs={"slug": self.object.book.slug},
        )
