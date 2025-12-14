from django.urls import path
from . import views

app_name = 'staff'  # ← ADD THIS

urlpatterns = [
    path('login/', views.staff_login, name='login'),
    path('logout/', views.staff_logout, name='logout'),
    path('', views.dashboard, name='dashboard'),
    path('feed/', views.feed, name='feed'),
    path('pet/<int:pet_id>/sheet/', views.pet_sheet, name='pet_sheet'),
]
