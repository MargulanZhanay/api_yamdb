from django_filters import rest_framework as filters

from reviews.models import Title


class TitleFitler(filters.FilterSet):
    """Фильтры произведений."""

    name = filters.CharFilter(field_name="name", lookup_expr="contains")
    year = filters.NumberFilter(field_name="year", lookup_expr="contains")
    category = filters.CharFilter(
        field_name="category__slug", lookup_expr="contains"
    )
    genre = filters.CharFilter(
        field_name="genre__slug", lookup_expr="contains"
    )

    class Meta:
        model = Title
        fields = "__all__"
