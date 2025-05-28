from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_page, name='login'),
    path('logout/', views.logout_user, name='logout'),   # Logout functionality
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    path('manage_organization/', views.manage_organization, name='add_organization'),  # For adding
    path('manage_organization/<int:org_id>/', views.manage_organization, name='update_organization'), 
    path('delete_organization/<int:org_id>/', views.delete_organization, name='delete_organization'),
    path('add_role/', views.add_role, name='add_role'),
    path('user/<int:user_id>/', views.add_update_user, name='update_user'),
    path('user/add/', views.add_update_user, name='add_user'),
    path('user/delete/<int:user_id>/', views.delete_user, name='delete_user'),

]