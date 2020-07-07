from django.urls import path
from django.views.decorators.cache import cache_page
from django.contrib.sitemaps.views import sitemap
from django.contrib.sitemaps import views as sitemaps_views
from .sitemap import *

from . import views
from django.views.generic import RedirectView, TemplateView

sitemaps = {
    'static': StaticViewSitemap,
    'users': UserSitemap,
}


urlpatterns = [
    path('', views.index, name='index'),
    path('my_profile', views.my_profile, name='my_profile'),
    path('logout', views.logout_view, name='logout_view'),
    path('rust-stats/user/<int:user_id>', views.user_profile, name='user_profile'),
    path('rust-stats/user-stats/<int:user_id>', views.user_stats, name='user_stats'),
    path('rust-stats/user-friends/<int:user_id>', views.user_friends, name='user_friends'),
    path('rust-stats/ban-user', views.ban_user, name='ban_user'),
    path('rust-stats/delete-user', views.delete_user, name='delete_user'),
    path('discord-bot', views.discord_bot_page, name='discord_bot_page'),
    path('invite-bot', RedirectView.as_view(url='https://discord.com/oauth2/authorize?client_id=727206959287107586&scope=bot&permissions=92240'), name='invite_bot'),
    # 4 hours cache time for sitemaps
    path('sitemap.xml',  cache_page(14400)(sitemaps_views.index), {'sitemaps': sitemaps, 'sitemap_url_name': 'sitemaps'}),
    path('sitemap-<section>.xml', cache_page(14400)(sitemaps_views.sitemap), {'sitemaps': sitemaps}, name='sitemaps'),
    path("robots.txt", TemplateView.as_view(template_name="rust_stats/robots.txt", content_type="text/plain")),
    path('delete_inactive_users', views.delete_inactive_users, name='delete_inactive_users'),
]
