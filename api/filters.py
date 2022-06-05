from django_filters.rest_framework import FilterSet
from .models import Event


class EventFilter(FilterSet):
    class Meta:
        model = Event
        fields = {
            'theme_id': ['exact'],
            'unit_price': ['gt', 'lt']
        }
