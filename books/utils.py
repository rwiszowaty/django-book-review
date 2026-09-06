from decimal import Decimal, ROUND_HALF_UP


def get_rating_stars(rating):
    if rating is None:
        return []

    rounded_rating = (Decimal(str(rating)) * 2).quantize(
        Decimal("1"),
        rounding=ROUND_HALF_UP,
    ) / 2

    full_stars = int(rounded_rating)
    half_star = rounded_rating % 1 == Decimal("0.5")
    empty_stars = 5 - full_stars - int(half_star)

    return (
        ["bi-star-fill"] * full_stars
        + (["bi-star-half"] if half_star else [])
        + ["bi-star"] * empty_stars
    )
