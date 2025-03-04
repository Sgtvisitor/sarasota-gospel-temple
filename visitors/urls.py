from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Home page
    path('visitor-form/', views.visitor_form, name='visitor_form'),  # Visitor form
    path('contact/', views.contact, name='contact'),  # Contact page
    path('success/', views.success, name='success'),  # Success page
    path('api/visitors/', views.get_visitors, name='get_visitors'),  # API to fetch visitors
    path('api/save-visitor/', views.save_visitor, name='save_visitor'),  # API to save visitor
    path('api/delete-visitor/', views.delete_visitor, name='delete_visitor'),  # API to delete visitor
    path('accounts/login/', auth_views.LoginView.as_view(template_name='visitors/login.html'), name='login'),  # Custom login
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),  # Logout
]