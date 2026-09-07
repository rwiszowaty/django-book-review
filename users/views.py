from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import DetailView, FormView, TemplateView

from .forms import UsernameForm
from .models import CustomUser

from books.utils import get_rating_stars


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

        reviews = self.request.user.reviews.select_related(
            "book",
        ).all()

        for review in reviews:
            review.rating_stars = get_rating_stars(review.rating)

        context["profile_user"] = self.request.user
        context["reviews"] = reviews
        context["review_count"] = reviews.count()

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


class PublicProfileView(DetailView):
    model = CustomUser
    template_name = "public_profile.html"
    context_object_name = "profile_user"
    slug_field = "username"
    slug_url_kwarg = "username"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        reviews = self.object.reviews.select_related(
            "book",
        ).all()

        for review in reviews:
            review.rating_stars = get_rating_stars(
                review.rating,
            )

        context["reviews"] = reviews
        context["review_count"] = reviews.count()

        return context
