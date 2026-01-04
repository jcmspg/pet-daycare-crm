from django.urls import path
from . import views
from .auth_helpers import smart_redirect

app_name = 'home'

urlpatterns = [
    path('', views.home, name='index'),
    path('tutors/', views.tutor_entry, name='tutor_entry'),
    path('businesses/', views.business_entry, name='business_entry'),
    path('for-pet-parents/', views.for_pet_parents, name='for_pet_parents'),
    path('for-businesses/', views.for_businesses, name='for_businesses'),
    path('invite/<uuid:invitation_id>/', views.accept_invitation, name='accept_invitation'),
    path('dashboard/', smart_redirect, name='dashboard_redirect'),
    path('error/', views.error_page, name='error'),
    path('error/access-denied/', views.permission_denied, name='permission_denied'),
]