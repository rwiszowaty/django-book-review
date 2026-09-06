import pytest

from books.utils import get_rating_stars


class TestGetRatingStars:
    def test_returns_empty_list_for_none(self):
        assert get_rating_stars(None) == []

    @pytest.mark.parametrize(
        "rating, expected",
        [
            (
                1,
                [
                    "bi-star-fill",
                    "bi-star",
                    "bi-star",
                    "bi-star",
                    "bi-star",
                ],
            ),
            (
                2,
                [
                    "bi-star-fill",
                    "bi-star-fill",
                    "bi-star",
                    "bi-star",
                    "bi-star",
                ],
            ),
            (
                3,
                [
                    "bi-star-fill",
                    "bi-star-fill",
                    "bi-star-fill",
                    "bi-star",
                    "bi-star",
                ],
            ),
            (
                4,
                [
                    "bi-star-fill",
                    "bi-star-fill",
                    "bi-star-fill",
                    "bi-star-fill",
                    "bi-star",
                ],
            ),
            (
                5,
                [
                    "bi-star-fill",
                    "bi-star-fill",
                    "bi-star-fill",
                    "bi-star-fill",
                    "bi-star-fill",
                ],
            ),
        ],
    )
    def test_returns_correct_stars_for_integer_rating(
        self,
        rating,
        expected,
    ):
        assert get_rating_stars(rating) == expected

    @pytest.mark.parametrize(
        "rating, expected",
        [
            (
                1.5,
                [
                    "bi-star-fill",
                    "bi-star-half",
                    "bi-star",
                    "bi-star",
                    "bi-star",
                ],
            ),
            (
                2.5,
                [
                    "bi-star-fill",
                    "bi-star-fill",
                    "bi-star-half",
                    "bi-star",
                    "bi-star",
                ],
            ),
            (
                3.5,
                [
                    "bi-star-fill",
                    "bi-star-fill",
                    "bi-star-fill",
                    "bi-star-half",
                    "bi-star",
                ],
            ),
            (
                4.5,
                [
                    "bi-star-fill",
                    "bi-star-fill",
                    "bi-star-fill",
                    "bi-star-fill",
                    "bi-star-half",
                ],
            ),
        ],
    )
    def test_returns_correct_stars_for_half_rating(
        self,
        rating,
        expected,
    ):
        assert get_rating_stars(rating) == expected
