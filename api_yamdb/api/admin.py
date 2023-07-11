from django.contrib import admin

from reviews.models import Category, Genre, Title, User  # isort: skip


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
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


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug',
    )
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug',
    )
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'category',
        'name',
        'year',
        'description'
    )
    search_fields = ('name',)
    list_filter = ('year', 'category', 'genre')
    empty_value_display = '-пусто-'
