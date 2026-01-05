from django.urls import path
from . import views

app_name = 'tutor'

urlpatterns = [
    path('', views.tutor_dashboard, name='dashboard'),
    path('profile/', views.tutor_profile, name='profile'),
    path('pet/create/', views.create_pet, name='create_pet'),
    path('pet/<int:pet_id>/', views.tutor_pet_sheet, name='pet_sheet'),
]