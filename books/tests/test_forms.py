import pytest

from books.forms import ReviewForm


class TestReviewForm:
    def test_review_form_is_valid(self):
        form = ReviewForm(
            data={
                "content": "Example of book review.",
                "rating": 5,
            }
        )

        assert form.is_valid()

    def test_review_form_does_not_include_book_or_user(self):
        form = ReviewForm()

        assert "book" not in form.fields
        assert "user" not in form.fields

    @pytest.mark.parametrize("rating", [1, 2, 3, 4, 5])
    def test_review_form_accepts_valid_rating(self, rating):
        form = ReviewForm(
            data={
                "content": "Example of book review.",
                "rating": rating,
            }
        )

        assert form.is_valid()

    @pytest.mark.parametrize("rating", [0, 6])
    def test_review_form_rejects_invalid_rating(self, rating):
        form = ReviewForm(
            data={
                "content": "Example of book review.",
                "rating": rating,
            }
        )

        assert not form.is_valid()
