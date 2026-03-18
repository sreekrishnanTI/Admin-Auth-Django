from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('panel/users/', views.user_list, name='user_list'),
    path('panel/users/create/', views.user_create, name='user_create'),
    path('panel/users/<int:user_id>/edit/', views.user_update, name='user_update'),
    path("panel/users/<int:user_id>/toggle/", views.user_toggle_active, name="user_toggle_active"),
]