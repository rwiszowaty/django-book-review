from django.shortcuts import get_object_or_404

from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveAPIView
from drf_spectacular.utils import extend_schema, extend_schema_view

from books.models import Book, Review
from .permissions import HasUsername
from .serializers import BookSerializer, ReviewSerializer


@extend_schema(
    summary="List books",
    description="Returns a list of available books.",
)
class BookListApiView(ListAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer


@extend_schema(
    summary="Retrieve a book",
    description="Returns detailed information about a book.",
)
class BookDetailApiView(RetrieveAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    lookup_field = "slug"


@extend_schema_view(
    get=extend_schema(
        summary="List book reviews",
        description=("Return all reviews for a book."),
        responses={
            200: ReviewSerializer,
            400: {"description": "Book not found."},
        },
    ),
    post=extend_schema(
        summary="Create a book review.",
        description=(
            "Create a review for a book. "
            "Authenticated users with a username can create a review."
        ),
        request=ReviewSerializer,
        responses={
            201: ReviewSerializer,
            400: {"description": "Invalid review data."},
            404: {"description": "Book not found."},
        },
    ),
)
class BookReviewListCreateApiView(ListCreateAPIView):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        return Review.objects.filter(
            book__slug=self.kwargs["slug"],
        ).select_related("user")

    def perform_create(self, serializer):
        book = get_object_or_404(
            Book,
            slug=self.kwargs["slug"],
        )

        if Review.objects.filter(
            book=book,
            user=self.request.user,
        ).exists():
            raise ValidationError(
                "Użytkownik może dodać tylko jedną recenzję do książki."
            )

        serializer.save(
            user=self.request.user,
            book=book,
        )

    def get_permissions(self):
        if self.request.method == "POST":
            return [HasUsername()]

        return []
