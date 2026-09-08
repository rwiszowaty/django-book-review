from django.db.models import Avg
from rest_framework import serializers

from books.models import Book, Review


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
