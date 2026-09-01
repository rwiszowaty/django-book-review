from django import forms

from .models import Review


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ("content", "rating")
        widgets = {
            "content": forms.Textarea(
                attrs={
                    "rows": 5,
                    "placeholder": "Napisz swoją recenzję...",
                }
            )
        }
