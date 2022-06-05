from dataclasses import field
from .models import Event, EventImage, Theme, Cart, CartTicket, Order, OrderTicket, Customer
from rest_framework import serializers
from django.db import transaction


class EventImageSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        event_id = self.context['event_id']
        return EventImage.objects.create(event_id=event_id, **validated_data)

    class Meta:
        model = EventImage
        fields = ['id', 'image']


class EventSerializer(serializers.ModelSerializer):
    images = EventImageSerializer(many=True, read_only=True)

    class Meta:
        model = Event
        fields = ['id', 'title', 'slug', 'description',
                  'inventory', 'unit_price', 'theme', 'city', 'location', 'date', 'images', 'last_update']


class ThemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Theme
        fields = ['id', 'title', 'events_count']

    events_count = serializers.IntegerField(read_only=True)


class SimpleEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['id', 'title', 'unit_price']


class CartTicketSerializer(serializers.ModelSerializer):
    event = SimpleEventSerializer()
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, cart_ticket: CartTicket):
        return cart_ticket.quantity * cart_ticket.event.unit_price

    class Meta:
        model = CartTicket
        fields = ['id', 'event', 'quantity', 'total_price']


class CartSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    tickets = CartTicketSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, cart):
        return sum([ticket.quantity * ticket.event.unit_price for ticket in cart.tickets.all()])

    class Meta:
        model = Cart
        fields = ['id', 'tickets', 'total_price']


class AddCartTicketSerializer(serializers.ModelSerializer):
    event_id = serializers.IntegerField()

    def validate_event_id(self, value):
        if not Event.objects.filter(pk=value).exists():
            raise serializers.ValidationError(
                'No event with the given ID was found.')
        return value

    def save(self, **kwargs):
        cart_id = self.context['cart_id']
        event_id = self.validated_data['event_id']
        quantity = self.validated_data['quantity']

        try:
            cart_ticket = CartTicket.objects.get(
                cart_id=cart_id, event_id=event_id)
            cart_ticket.quantity += quantity
            cart_ticket.save()
            self.instance = cart_ticket
        except CartTicket.DoesNotExist:
            self.instance = CartTicket.objects.create(
                cart_id=cart_id, **self.validated_data)

        return self.instance

    class Meta:
        model = CartTicket
        fields = ['id', 'event_id', 'quantity']


class UpdateCartTicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartTicket
        fields = ['quantity']


class CustomerSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Customer
        fields = ['id', 'user_id', 'phone', 'city', 'country']


class OrderTicketSerializer(serializers.ModelSerializer):
    event = SimpleEventSerializer()

    class Meta:
        model = OrderTicket
        fields = ['id', 'event', 'unit_price', 'quantity']


class OrderSerializer(serializers.ModelSerializer):
    tickets = OrderTicketSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'customer', 'placed_at', 'payment_status', 'tickets']


class UpdateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['payment_status']


class CreateOrderSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()

    def validate_cart_id(self, cart_id):
        if not Cart.objects.filter(pk=cart_id).exists():
            raise serializers.ValidationError(
                'No cart with the given ID was found.')
        if CartTicket.objects.filter(cart_id=cart_id).count() == 0:
            raise serializers.ValidationError('The cart is empty.')
        return cart_id

    def save(self, **kwargs):
        with transaction.atomic():
            cart_id = self.validated_data['cart_id']

            customer = Customer.objects.get(
                user_id=self.context['user_id'])
            order = Order.objects.create(customer=customer)

            cart_tickets = CartTicket.objects \
                .select_related('event') \
                .filter(cart_id=cart_id)
            order_tickets = [
                OrderTicket(
                    order=order,
                    event=ticket.event,
                    unit_price=ticket.event.unit_price,
                    quantity=ticket.quantity
                ) for ticket in cart_tickets
            ]
            OrderTicket.objects.bulk_create(order_tickets)

            Cart.objects.filter(pk=cart_id).delete()

            return order
