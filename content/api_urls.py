from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import BlogViewSet, ResearchViewSet, ImageAssetViewSet

router = DefaultRouter()
router.register(r"blogs", BlogViewSet, basename="blog")
router.register(r"research", ResearchViewSet, basename="research")
router.register(r"images", ImageAssetViewSet, basename="images")

urlpatterns = [
    path("auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("", include(router.urls)),
]
