import re

from django.db import models

# Create your models here.


class Author(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    bio = models.TextField(blank=True)
    birth_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["last_name", "first_name"]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    isbn = models.CharField(max_length=13, unique=True)
    publication_date = models.DateField(null=True, blank=True)
    pages = models.PositiveIntegerField(null=True, blank=True)
    cover = models.ImageField(
        upload_to="book_covers/",
        blank=True,
    )

    authors = models.ManyToManyField(
        Author,
        related_name="books",
    )

    genres = models.ManyToManyField(
        Genre,
        related_name="books",
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.isbn = re.sub(r"[-\s]", "", self.isbn)
        super().save(*args, **kwargs)
