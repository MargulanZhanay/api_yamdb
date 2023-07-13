from django.core.exceptions import ValidationError
from django.utils import timezone


def year_validator(year):
    current_year = timezone.now().year
    if year > current_year:
        raise ValidationError(
            f'Год выпуска не может быть больше {current_year}'
        )