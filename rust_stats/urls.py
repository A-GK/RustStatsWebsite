from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('rust-stats/user/<int:user_id>', views.user_profile, name='user_profile'),
    path('rust-stats/user-stats/<int:user_id>', views.user_stats, name='user_stats'),
]