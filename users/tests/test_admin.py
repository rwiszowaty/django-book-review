import pytest
from django.contrib import admin

from users.admin import CustomUserAdmin
from users.models import CustomUser


@pytest.mark.django_db
def test_custom_user_is_registered_in_admin():
    assert isinstance(
        admin.site._registry[CustomUser],
        CustomUserAdmin,
    )


@pytest.mark.django_db
def test_custom_user_admin_uses_email():
    admin_instance = admin.site._registry[CustomUser]

    fields = []

    for fieldset in admin_instance.add_fieldsets:
        fields.extend(fieldset[1]["fields"])

    assert "email" in fields


@pytest.mark.django_db
def test_custom_user_admin_does_not_use_username():
    admin_instance = admin.site._registry[CustomUser]

    fields = []

    for fieldset in admin_instance.add_fieldsets:
        fields.extend(fieldset[1]["fields"])

    assert "username" not in fields


@pytest.mark.django_db
def test_custom_user_admin_list_display():
    admin_instance = admin.site._registry[CustomUser]

    assert admin_instance.list_display == (
        "email",
        "is_staff",
        "is_active",
    )


@pytest.mark.django_db
def test_custom_user_admin_search_fields():
    admin_instance = admin.site._registry[CustomUser]

    assert admin_instance.search_fields == ("email",)
