from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import FormView, TemplateView

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


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = "profile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["profile_user"] = self.request.user
        context["reviews"] = self.request.user.reviews.select_related(
            "book",
        ).all()
        return context


class ProfileEditView(LoginRequiredMixin, FormView):
    template_name = "profile_edit.html"
    form_class = UsernameForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["instance"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("users:profile")
