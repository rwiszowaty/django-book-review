from rest_framework.generics import ListAPIView, RetrieveAPIView

from books.models import Book
from .serializers import BookSerializer


class BookListApiView(ListAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer


class BookDetailApiView(RetrieveAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    lookup_field = "slug"
