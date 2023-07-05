from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


class UserAdmin(UserAdmin):
    list_display = (
        'first_name',
        'last_name',
        'username',
        'role',
        'email',
        'bio'
        )
    list_editable = ('role',)
    search_fields = ('username',)
    empty_value_display = '-пусто-'


admin.site.register(User, UserAdmin)