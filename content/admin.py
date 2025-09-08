from django.contrib import admin
from .models import Blog, Research, ImageAsset

@admin.register(ImageAsset)
class ImageAssetAdmin(admin.ModelAdmin):
    list_display = ("id", "alt_text", "file", "created_at")
    search_fields = ("alt_text", "file")

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ("title", "status", "published_at", "author", "updated_at")
    list_filter = ("status", "published_at", "author")
    search_fields = ("title", "summary", "slug")
    autocomplete_fields = ("featured_image", "author")
    readonly_fields = ("created_at", "updated_at",)
    prepopulated_fields = {"slug": ("title",)}

@admin.register(Research)
class ResearchAdmin(admin.ModelAdmin):
    list_display = ("title", "status", "updated_at")
    list_filter = ("status",)
    search_fields = ("title", "slug", "description")
    autocomplete_fields = ("featured_image",)
    readonly_fields = ("created_at", "updated_at",)
    prepopulated_fields = {"slug": ("title",)}
