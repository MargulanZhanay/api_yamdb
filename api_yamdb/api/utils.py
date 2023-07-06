from rest_framework.filters import SearchFilter
from rest_framework.mixins import (CreateModelMixin, DestroyModelMixin,
                                   ListModelMixin)
from rest_framework.viewsets import GenericViewSet


class CategoryGenreMixinSet(CreateModelMixin, DestroyModelMixin,
                            ListModelMixin, GenericViewSet):
    permission_classes = ()
    filter_backends = (SearchFilter)
    search_fields = ('name', )
    lookup_field = 'slug'
