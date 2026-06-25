from django.urls import path
from .views import PlatformWalletView, RecentDepositsView
from .webhooks.alchemy import alchemy_webhook
from .webhooks.blockcypher import blockcypher_webhook

urlpatterns = [
    path("platform-wallet/",      PlatformWalletView.as_view(),  name="platform-wallet"),
    path("deposits/",             RecentDepositsView.as_view(),   name="core-deposits"),
    path("webhooks/alchemy/",     alchemy_webhook,                name="webhook-alchemy"),
    path("webhooks/blockcypher/", blockcypher_webhook,            name="webhook-blockcypher"),
]