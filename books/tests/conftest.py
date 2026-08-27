import io

import pytest
from PIL import Image

from django.core.files.uploadedfile import SimpleUploadedFile

from books.models import Author, Book, Genre


@pytest.fixture
def author():
    return Author.objects.create(
        first_name="Robert",
        last_name="Jordan",
    )


@pytest.fixture
def second_author():
    return Author.objects.create(
        first_name="Brandon",
        last_name="Sanderson",
    )


@pytest.fixture
def genre():
    return Genre.objects.create(
        name="Fantasy",
        slug="fantasy",
    )


@pytest.fixture
def book():
    return Book.objects.create(
        title="The great hunt",
        slug="the-great-hunt",
        isbn="1234567890123",
    )


@pytest.fixture
def image_file():
    image = Image.new("RGB", (100, 100), "white")

    file = io.BytesIO()
    image.save(file, format="JPEG")
    file.seek(0)

    return SimpleUploadedFile(
        name="cover.jpg",
        content=file.getvalue(),
        content_type="image/jpeg",
    )


@pytest.fixture
def media_root(tmp_path, settings):
    settings.MEDIA_ROOT = tmp_path
    return tmp_path
