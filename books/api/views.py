from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveAPIView

from books.models import Book, Review
from .permissions import HasUsername
from .serializers import BookSerializer, ReviewSerializer


class BookListApiView(ListAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer


class BookDetailApiView(RetrieveAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    lookup_field = "slug"


class BookReviewListCreateApiView(ListCreateAPIView):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        return Review.objects.filter(
            book__slug=self.kwargs["slug"],
        ).select_related("user")

    def perform_create(self, serializer):
        book = Book.objects.get(
            slug=self.kwargs["slug"],
        )

        serializer.save(
            user=self.request.user,
            book=book,
        )

    def get_permissions(self):
        if self.request.method == "POST":
            return [HasUsername()]

        return []
