from django.urls import path
from django.conf.urls import handler404
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.sitemaps.views import sitemap

from . import views
from .sitemap import AdSitemap, StaticSitemap

app_name = 'cardealer'

sitemaps = {
    'ad': AdSitemap,
    'static': StaticSitemap
}

urlpatterns = [
    path('', views.index_request, name='index'),
    path('login/', views.login_request, name='login'),
    path('logout/', views.logout_request, name='logout'),
    path('register/', views.register_request, name='register'),
    path('listing/', views.listing_request, name='listing'),
    path('post-ad/', views.post_ad_request, name='post-ad'),
    path('profile/', views.profile_request, name='profile'),
    path('detail/<uuid:pk>/', views.detail_request, name='detail'),
    path('deactive/', views.deactive_request, name='deactive'),
    path('uploads/', views.upload_request, name='uploads'),
    path('getmodels/', views.getmodels_request, name='getmodels'),
    path('sendmail/', views.sendmail_request, name='sendmail'),
    path('trovit-feed.xml', views.gettrovitxml_request, name='gettrovitxml'),
    path('oodle-feed.xml', views.getoodlexml_request, name='getoodlexml'),
    path('locanto-feed.xml', views.getlocantoxml_request, name='getlocantoxml'),
    path('ooyyo-feed.xml', views.getooyyoxml_request, name='getooyyoxml'),
    path('contact/', views.contact_request, name='contact'),
    path('terms/', views.terms_request, name='terms'),
    path('safety/', views.safety_request, name='safety'),
    path('privacy/', views.privacy_request, name='privacy'),
    path('delete/<uuid:pk>/', views.delete_request, name='delete'),
    path('edit/<uuid:pk>/', views.edit_request, name='edit'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'cardealer.views.error_404'
