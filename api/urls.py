from django.urls import path
from rest_framework_nested import routers
from . import views

router = routers.DefaultRouter()
router.register('events', views.EventViewSet, basename='events')
router.register('themes', views.ThemeViewSet)
router.register('carts', views.CartViewSet)
router.register('customers', views.CustomerViewSet)
router.register('orders', views.OrderViewSet, basename='orders')

events_router = routers.NestedDefaultRouter(router, 'events', lookup='event')
events_router.register('images', views.EventImageViewSet,
                       basename='event-images')

carts_router = routers.NestedDefaultRouter(router, 'carts', lookup='cart')
carts_router.register('tickets', views.CartTicketViewSet,
                      basename='cart-tickets')

# URLConf
urlpatterns = router.urls + events_router.urls + carts_router.urls
