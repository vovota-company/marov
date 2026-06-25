from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework_simplejwt.views import TokenRefreshView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # schema + docs 
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema')),

    # JWT refresh 
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # accounts 
    path('api/auth/', include('accounts.urls')),

    # chat 
    path('api/chat/',include('chat.urls')),

    # kyc
    path('api/kyc/',include('kyc.urls')),

    # deposit
    path('api/deposit/',include('deposit.urls')),

    # withdraw 
    path('api/withdraw/',include('withdraw.urls')),

    # core
    path('api/core/',include('core.urls')),

    # p2p
    path('api/p2p/',include('p2p.urls')),

    # wallet
    path('api/wallet/',include('wallet.urls')),

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)