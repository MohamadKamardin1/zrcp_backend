from django.contrib import admin
from .models import Blog, Research, ImageAsset
from django.contrib.auth import get_user_model

User = get_user_model()

@admin.register(ImageAsset)
class ImageAssetAdmin(admin.ModelAdmin):
    list_display = ("id", "alt_text", "file", "created_at")
    search_fields = ("alt_text", "file")


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ("title", "status", "published_at", "author", "updated_at")
    list_filter = ("status", "published_at", "author")
    search_fields = ("title", "summary", "slug")
    
    # ✅ Only include ForeignKey fields in autocomplete_fields
    autocomplete_fields = ("author",)  # 'featured_image' is now ImageField, not FK
    
    readonly_fields = ("created_at", "updated_at",)
    prepopulated_fields = {"slug": ("title",)}


@admin.register(Research)
class ResearchAdmin(admin.ModelAdmin):
    list_display = ("title", "status", "updated_at")
    list_filter = ("status",)
    search_fields = ("title", "slug", "description")
    
    # ✅ Removed 'featured_image' from autocomplete_fields since it's now an ImageField
    autocomplete_fields = ()  # or remove this line entirely
    
    readonly_fields = ("created_at", "updated_at",)
    prepopulated_fields = {"slug": ("title",)}
