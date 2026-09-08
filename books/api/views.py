from rest_framework.generics import ListAPIView, RetrieveAPIView

from books.models import Book, Review
from .serializers import BookSerializer, ReviewSerializer


class BookListApiView(ListAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer


class BookDetailApiView(RetrieveAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    lookup_field = "slug"


class BookReviewListApiView(ListAPIView):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        return Review.objects.filter(
            book__slug=self.kwargs["slug"],
        ).select_related("user")
