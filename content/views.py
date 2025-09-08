from rest_framework import viewsets, permissions, filters
from .models import Blog, Research, ImageAsset
from .serializers import BlogSerializer, ResearchSerializer, ImageAssetSerializer

class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff

class ImageAssetViewSet(viewsets.ModelViewSet):
    queryset = ImageAsset.objects.all().order_by("-created_at")
    serializer_class = ImageAssetSerializer
    permission_classes = [IsAdminOrReadOnly]


class BlogViewSet(viewsets.ModelViewSet):
    queryset = Blog.objects.select_related("author", "featured_image").all()
    serializer_class = BlogSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "summary", "slug"]
    ordering_fields = ["published_at", "created_at"]
    ordering = ["-published_at", "-created_at"]

    def get_queryset(self):
        qs = super().get_queryset()
        # Public can see only published; staff sees all
        if not (self.request.user and self.request.user.is_staff):
            qs = qs.filter(status="published")
        return qs


class ResearchViewSet(viewsets.ModelViewSet):
    queryset = Research.objects.select_related("featured_image").all()
    serializer_class = ResearchSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "description", "slug"]
    ordering_fields = ["created_at", "updated_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        qs = super().get_queryset()
        if not (self.request.user and self.request.user.is_staff):
            qs = qs.filter(status="published")
        return qs
