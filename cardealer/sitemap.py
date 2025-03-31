from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import Ad

class StaticSitemap(Sitemap):
    changefreq = 'yearly'
    priority = 1
    protocol = 'https'

    def items(self):
        return ['cardealer:index', 'cardealer:login', 'cardealer:listing', 'cardealer:contact', 'cardealer:terms', 'cardealer:safety', 'cardealer:privacy']

    def location(self, item):
        return reverse(item)

class AdSitemap(Sitemap):
    changefreq = 'daily'
    priority = 0.8
    protocol = 'https'

    def items(self):
        return Ad.objects.order_by('-date_posted')

    def lastmod(self, obj):
        return obj.date_posted
