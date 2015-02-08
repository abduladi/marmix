# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.views.generic import TemplateView

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()
import permission
permission.autodiscover()

urlpatterns = patterns('',
    url(r'^$',  # noqa
        TemplateView.as_view(template_name='pages/home.html'),
        name="home"),
    url(r'^about/$',
        TemplateView.as_view(template_name='pages/about.html'),
        name="about"),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    # User management
    url(r'^users/', include("users.urls", namespace="users")),
    url(r'^accounts/', include('allauth.urls')),

    # Uncomment the next line to enable avatars
    url(r'^avatar/', include('avatar.urls')),

    # MarMix apps urls
    url(r'^stocks/', include('stocks.urls')),
    url(r'^customers/', include('customers.urls')),
    url(r'^simulations/', include('simulations.urls')),
    url(r'^tickers/', include('tickers.urls')),

) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

from django.conf.urls import url, include
from simulations.views import SimulationViewSet, CurrencyViewSet, TeamViewSet, ClockViewSet
from stocks.views import StockViewSet, QuoteViewSet, OrderViewSet, HoldingsViewSet, CreateOrderViewSet
from users.views import UserViewSet, LoginView
from tickers.views import CompaniesViewSet
from rest_framework.routers import DefaultRouter


# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'simulations', SimulationViewSet)
router.register(r'currencies', CurrencyViewSet)
router.register(r'users', UserViewSet)
router.register(r'stocks', StockViewSet, base_name='stock')
router.register(r'quotes', QuoteViewSet)
router.register(r'teams', TeamViewSet)
router.register(r'orders', OrderViewSet, base_name='order')
router.register(r'order', CreateOrderViewSet, base_name='create-order')
router.register(r'holdings', HoldingsViewSet, base_name='holdings')
router.register(r'clock', ClockViewSet, base_name='clock')
router.register(r'tickers', CompaniesViewSet, base_name='ticker')

# The API URLs are now determined automatically by the router.
# Additionally, we include the login URLs for the browsable API.
urlpatterns += [
    url(r'^api/v1/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api/v1/auth/login/$', LoginView.as_view(), name='login'),
]