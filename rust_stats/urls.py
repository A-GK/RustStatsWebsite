from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('my_profile', views.my_profile, name='my_profile'),
    path('logout', views.logout_view, name='logout_view'),
    path('rust-stats/user/<int:user_id>', views.user_profile, name='user_profile'),
    path('rust-stats/user-stats/<int:user_id>', views.user_stats, name='user_stats'),
    path('rust-stats/user-friends/<int:user_id>', views.user_friends, name='user_friends'),
    path('rust-stats/ban-user', views.ban_user, name='ban_user'),
    path('rust-stats/delete-user', views.delete_user, name='delete_user'),
]