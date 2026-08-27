from django.contrib import admin

from .models import Author, Book, Genre


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name")
    search_fields = ("first_name", "last_name")
    ordering = ("last_name", "first_name")


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "isbn",
        "publication_date",
        "pages",
        "created_at",
    )
    search_fields = (
        "title",
        "isbn",
        "authors__first_name",
        "authors__last_name",
    )
    list_filter = ("genres", "publication_date")
    filter_horizontal = ("authors", "genres")
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "publication_date"
    readonly_fields = ("created_at", "updated_at")
