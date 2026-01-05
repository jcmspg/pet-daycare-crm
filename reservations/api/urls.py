"""
API URLs for Reservations app
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ServiceBookingViewSet, ServiceSlotViewSet

router = DefaultRouter()
router.register(r'bookings', ServiceBookingViewSet, basename='booking')
router.register(r'slots', ServiceSlotViewSet, basename='slot')

urlpatterns = [
    path('', include(router.urls)),
]
