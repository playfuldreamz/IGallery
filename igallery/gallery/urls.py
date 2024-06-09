from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('instagram/login/', views.instagram_login, name='instagram_login'),
    path('instagram/callback/', views.instagram_callback, name='instagram_callback'),
    path('gallery/', views.gallery, name='gallery'),
    path('saved_pictures/', views.saved_pictures, name='saved_pictures'),
]