from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.home, name='home'),
    path('download/<int:file_id>/', views.download_file, name='download_file'),
]