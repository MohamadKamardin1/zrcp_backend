from rest_framework import serializers
from .models import Blog, Research, ImageAsset
from django.utils import timezone

class ImageAssetSerializer(serializers.ModelSerializer):
    # Return the full Cloudinary URL for the file
    file = serializers.SerializerMethodField()

    class Meta:
        model = ImageAsset
        fields = ["id", "file", "alt_text"]

    def get_file(self, obj):
        if obj.file:
            # obj.file is a CloudinaryResource object with url attribute
            return obj.file.url
        return None


class BlogSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.get_full_name", read_only=True)
    featured_image = ImageAssetSerializer(read_only=True)
    featured_image_id = serializers.PrimaryKeyRelatedField(
        queryset=ImageAsset.objects.all(), source="featured_image", write_only=True, required=False, allow_null=True
    )

    class Meta:
        model = Blog
        fields = [
            "id", "title", "slug", "author", "author_name",
            "featured_image", "featured_image_id",
            "summary", "body",
            "status", "published_at",
            "created_at", "updated_at",
        ]
        read_only_fields = ["slug", "created_at", "updated_at"]

    def validate_body(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("Body must be a list of blocks.")
        return value

    def validate(self, attrs):
        status = attrs.get("status", getattr(self.instance, "status", Blog.DRAFT))
        published_at = attrs.get("published_at", getattr(self.instance, "published_at", None))
        if status == Blog.PUBLISHED and not published_at:
            attrs["published_at"] = timezone.now()
        return attrs


class ResearchSerializer(serializers.ModelSerializer):
    featured_image = ImageAssetSerializer(read_only=True)
    featured_image_id = serializers.PrimaryKeyRelatedField(
        queryset=ImageAsset.objects.all(), source="featured_image", write_only=True, required=False, allow_null=True
    )
    # Serialize file field URLs properly if this is a CloudinaryField
    file = serializers.SerializerMethodField()

    class Meta:
        model = Research
        fields = [
            "id", "title", "slug",
            "featured_image", "featured_image_id",
            "description", "status", "file",
            "created_at", "updated_at",
        ]
        read_only_fields = ["slug", "created_at", "updated_at"]

    def get_file(self, obj):
        if obj.file:
            # If it's a CloudinaryField, return url
            try:
                return obj.file.url
            except Exception:
                return obj.file.name  # fallback to file name/path
        return None
