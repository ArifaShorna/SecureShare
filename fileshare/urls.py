from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('download/<int:file_id>/', views.download_file, name='download_file'),
    path('share/<int:file_id>/', views.share_file, name='share_file'),
    path('delete/<int:file_id>/', views.delete_file, name='delete_file'),
    path('unshare/<int:share_id>/', views.unshare_file, name='unshare_file'),
    path('preview/<int:file_id>/', views.preview_file, name='preview_file'),
]