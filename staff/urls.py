from django.urls import path
from . import views

app_name = 'staff'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('feed/', views.feed, name='feed'),
    path('pet/<int:pet_id>/sheet/', views.pet_sheet, name='pet_sheet'),]