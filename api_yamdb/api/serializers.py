"""Сериализаторы приложения api."""
from django.conf import settings
from django.core.validators import RegexValidator
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from reviews.models import Comments, Review, User

from titles.models import Category, Title, Genre
from .utils import generate_short_hash_mm3


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор модели Category."""
    class Meta:
        exclude = ('id',)
        model = Category
        lookup_field = 'slug'


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор модели Genre."""
    class Meta:
        exclude = ('id',)
        model = Genre
        lookup_field = 'slug'


class TitleGetSerializer(serializers.ModelSerializer):
    """Сериализатор вывода модели Title."""
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(
        read_only=True,
        many=True
    )
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Title
        fields = '__all__'

    def get_rating(self, title):
        reviews = title.reviews.all()
        if not reviews:
            return None
        total_score = sum(review.score for review in reviews)
        return total_score / len(reviews)


class TitlePostSerializer(serializers.ModelSerializer):
    """Сериализатор ввода модели Title."""
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug'
    )
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug',
        many=True
    )

    class Meta:
        model = Title
        fields = '__all__'


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор модели Review."""

    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')

    def validate(self, data):
        """Пользователь может оставить только один отзыв на произведение."""

        if self.context.get('request').method != 'POST':
            return data
        author = self.context.get('request').user
        title_id = self.context.get('view').kwargs.get('title_id')
        review = Review.objects.filter(title=title_id, author=author)
        if review.exists():
            raise serializers.ValidationError(
                'Вы уже оставили отзыв на это произведение.'
            )
        return data


class CommentsSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Comments."""

    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date')
        model = Comments


class RegistrationSerializer(serializers.ModelSerializer):
    """Сериализация регистрации пользователя и создания нового."""
    username = serializers.CharField(
        max_length=150,
        validators=[RegexValidator(r'^[\w.@+-]+\Z$', 'Некорректный формат.')])
    email = serializers.EmailField(max_length=254)

    class Meta:
        model = User
        fields = ('username', 'email')

    def create(self, validated_data):
        return User.objects.update_or_create(**validated_data)

    def validate(self, data):
        username = data.get('username')
        email = data.get('email')

        # Проверка запрещенных имен пользователя
        if username in settings.BANNED_USERNAMES:
            message = f'Имя пользователя {username} запрещено.'
            raise serializers.ValidationError(
                {'message': message})

        # Проверка занятости email другим пользователем
        user = User.objects.filter(email=email)
        if user.exists() and user[0].username != username:
            raise serializers.ValidationError(
                {'message':
                 f'Данный email={email} занят другим пользователем.'})

        # Проверка соответствия email пользователю
        user = User.objects.filter(username=username)
        if user.exists() and user[0].email != email:
            raise serializers.ValidationError(
                {'message':
                 f'У пользователя {user[0]} другой email.'})

        return data


class ConfirmRegistrationSerializer(serializers.ModelSerializer):
    """Подтверждение регистрации."""
    username = serializers.CharField()
    confirmation_code = serializers.CharField()

    class Meta:
        model = User
        fields = ('username', 'confirmation_code')

    def validate(self, data):
        username = data.get('username')
        user = get_object_or_404(User, username=username)
        confirmation_code = data.get('confirmation_code')

        # Если код невалидный выбрасываем исключение
        code = generate_short_hash_mm3(
            f'{user.username}{user.email}{user.updated_at}')
        if code != confirmation_code:
            raise serializers.ValidationError(
                {'message': 'Некорректный код.'})

        return {'username': user,
                'confirmation_code': confirmation_code}


class UserSerializer(serializers.ModelSerializer):
    """Получает пользователей списокм или создает нового."""
    username = serializers.CharField(
        max_length=150,
        validators=[RegexValidator(r'^[\w.@+-]+\Z$', 'Некорректный формат.')])

    class Meta:
        model = User
        fields = ('username', 'email',
                  'first_name', 'last_name',
                  'bio', 'role')

    def validate(self, data):
        username = data.get('username')

        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError(
                {'message':
                 'Пользователь уже существует.'})

        return data


class MeSerializer(serializers.ModelSerializer):
    """Пользователь может получить свои данные и поменять их."""
    username = serializers.CharField(
        max_length=150,
        validators=[RegexValidator(r'^[\w.@+-]+\Z$', 'Некорректный формат.')])
    role = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ('username', 'email',
                  'first_name', 'last_name',
                  'bio', 'role')
