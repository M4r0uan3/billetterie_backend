from django.contrib import admin, messages
from django.db.models.aggregates import Count
from django.db.models.query import QuerySet
from django.utils.html import format_html, urlencode
from django.urls import reverse
from . import models


class InventoryFilter(admin.SimpleListFilter):
    title = 'inventory'
    parameter_name = 'inventory'

    def lookups(self, request, model_admin):
        return [
            ('<10', 'Low')
        ]

    def queryset(self, request, queryset: QuerySet):
        if self.value() == '<10':
            return queryset.filter(inventory__lt=10)


class EventImageInline(admin.TabularInline):
    model = models.EventImage
    readonly_fields = ['thumbnail']

    def thumbnail(self, instance):
        if instance.image.name != '':
            return format_html(f'<img src="{instance.image.url}" class="thumbnail" />')
        return ''


@admin.register(models.Event)
class EventAdmin(admin.ModelAdmin):
    prepopulated_fields = {
        'slug': ['title']
    }
    actions = ['clear_inventory']
    list_display = ['title', 'unit_price',
                    'inventory_status', 'theme', 'date']
    list_editable = ['unit_price']
    list_filter = ['theme', 'last_update', InventoryFilter]
    list_per_page = 10
    inlines = [EventImageInline]
    list_select_related = ['theme']
    search_fields = ['title']

    @admin.display(ordering='inventory')
    def inventory_status(self, event):
        if event.inventory < 10:
            return 'Low'
        return 'OK'

    @admin.action(description='Clear inventory')
    def clear_inventory(self, request, queryset):
        updated_count = queryset.update(inventory=0)
        self.message_user(
            request,
            f'{updated_count} products were successfully updated.',
            messages.ERROR
        )

    class Media:
        css = {
            'all': ['api/styles.css']
        }


@admin.register(models.Theme)
class ThemeAdmin(admin.ModelAdmin):
    list_display = ['title']
    search_fields = ['title']

    @admin.display(ordering='events_count')
    def events_count(self, theme):
        url = (
            reverse('admin:api_event_changelist')
            + '?'
            + urlencode({
                'theme__id': str(theme.id)
            }))
        return format_html('<a href="{}">{} Events</a>', url, theme.events_count)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            events_count=Count('events')
        )


@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'email',
                    'orders', 'phone', 'city', 'country']
    list_editable = ['phone', 'city', 'country']
    list_select_related = ['user']
    list_per_page = 10
    ordering = ['user__first_name', 'user__last_name']
    search_fields = ['first_name__istartswith', 'last_name__istartswith']

    @admin.display(ordering='orders_count')
    def orders(self, customer):
        url = (
            reverse('admin:api_order_changelist')
            + '?'
            + urlencode({
                'customer__id': str(customer.id)
            }))
        return format_html('<a href="{}">{} Orders</a>', url, customer.orders_count)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            orders_count=Count('order')
        )


class OrderItemInline(admin.TabularInline):
    autocomplete_fields = ['event']
    min_num = 1
    max_num = 10
    model = models.OrderTicket
    extra = 0


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    autocomplete_fields = ['customer']
    inlines = [OrderItemInline]
    list_display = ['id', 'placed_at', 'customer', 'payment_status']
