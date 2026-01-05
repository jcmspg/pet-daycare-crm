from django.urls import path
from . import views

app_name = 'staff'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('feed/', views.feed, name='feed'),
    path('pet/<int:pet_id>/sheet/', views.pet_sheet, name='pet_sheet'),
    path('invite/create/', views.create_tutor_invitation, name='create_invitation'),
    path('invite/<uuid:invitation_id>/', views.show_invitation, name='show_invitation'),
    path('upload-banner/', views.upload_banner, name='upload_banner'),
]