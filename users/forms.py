from allauth.account.forms import AddEmailForm
from allauth.account.models import EmailAddress
from django import forms
from django.core.exceptions import ValidationError

from .models import CustomUser


class CustomAddEmailForm(AddEmailForm):
    def clean_email(self):
        email = super().clean_email()

        if (
            EmailAddress.objects.filter(
                email__iexact=email,
            )
            .exclude(
                user=self.user,
            )
            .exists()
        ):
            raise ValidationError("This email address is already in use.")

        return email


class UsernameForm(forms.ModelForm):
    username = forms.CharField(required=True)

    class Meta:
        model = CustomUser
        fields = ("username",)
