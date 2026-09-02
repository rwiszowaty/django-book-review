from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import FormView

from .forms import UsernameForm


class SetUsernameView(LoginRequiredMixin, FormView):
    template_name = "set_username.html"
    form_class = UsernameForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["instance"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("books:book_list")
