from django.contrib.sitemaps import Sitemap
from .models import User
from django.urls import reverse


class StaticViewSitemap(Sitemap):
    priority = 1
    protocol = "https"
    changefreq = "daily"

    def items(self):
        return ["index", "discord_bot_page"]

    def location(self, item):
        return reverse(item)


class UserSitemap(Sitemap):
    changefreq = "weekly"
    protocol = "https"
    limit = 500

    def items(self):
        return User.objects.filter(last_successful_update__isnull=False)
    
    def location(self, item):
        return "/rust-stats/user/" + str(item.user_id)