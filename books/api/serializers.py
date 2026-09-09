from django.db.models import Avg
from rest_framework import serializers
from drf_spectacular.utils import (
    extend_schema_field,
    extend_schema_serializer,
)

from books.models import Book, Review


@extend_schema_serializer(
    component_name="Book",
)
class BookSerializer(serializers.ModelSerializer):
    authors = serializers.StringRelatedField(many=True)
    genres = serializers.StringRelatedField(many=True)
    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = (
            "id",
            "title",
            "slug",
            "authors",
            "genres",
            "average_rating",
        )

    @extend_schema_field(float)
    def get_average_rating(self, obj):
        return obj.reviews.aggregate(
            average=Avg("rating"),
        )["average"]


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()

    class Meta:
        model = Review
        fields = (
            "id",
            "user",
            "content",
            "rating",
            "created_at",
            "updated_at",
        )

        read_only_fields = (
            "id",
            "user",
            "created_at",
            "updated_at",
        )
