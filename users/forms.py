from allauth.account.forms import AddEmailForm
from allauth.account.models import EmailAddress
from django.core.exceptions import ValidationError


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
