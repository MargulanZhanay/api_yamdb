from django.contrib import admin

from users.models import User  # isort: skip


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "first_name",
        "last_name",
        "username",
        "role",
        "email",
        "bio",
    )
    list_editable = ("role",)
    search_fields = ("username",)
    empty_value_display = "-пусто-"
