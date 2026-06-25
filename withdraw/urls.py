from rest_framework.routers import DefaultRouter
from .views import WithdrawViewSet

router = DefaultRouter()
router.register(r'', WithdrawViewSet, basename='withdraw')

urlpatterns = router.urls