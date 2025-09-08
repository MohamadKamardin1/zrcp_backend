from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify

User = get_user_model()

class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class ImageAsset(TimeStampedModel):
    """Reusable image (for blog inline images or research banners)."""
    file = models.ImageField(upload_to="uploads/")
    alt_text = models.CharField(max_length=255, blank=True, default="")

    def __str__(self):
        return self.alt_text or self.file.name


class Blog(TimeStampedModel):
    DRAFT = "draft"
    PUBLISHED = "published"
    STATUS_CHOICES = [(DRAFT, "Draft"), (PUBLISHED, "Published")]

    title = models.CharField(max_length=220)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    featured_image = models.ForeignKey(
        ImageAsset, on_delete=models.SET_NULL, null=True, blank=True, related_name="blogs_featured"
    )
    summary = models.TextField(blank=True, help_text="Short excerpt for listings/SEO")
    # Flexible content blocks stored as JSON:
    # Example: [{"type":"h2","text":"Intro"}, {"type":"p","text":"..."},
    #           {"type":"image","image_id": 3}, {"type":"h3","text":"..."}]
    body = models.JSONField(default=list, blank=True)

    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default=DRAFT)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-published_at", "-created_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)[:200]
            candidate = base
            i = 1
            while Blog.objects.filter(slug=candidate).exclude(pk=self.pk).exists():
                i += 1
                candidate = f"{base}-{i}"
            self.slug = candidate
        super().save(*args, **kwargs)


class Research(TimeStampedModel):
    DRAFT = "draft"
    IN_REVIEW = "in_review"
    PUBLISHED = "published"
    STATUS_CHOICES = [(DRAFT, "Draft"), (IN_REVIEW, "In Review"), (PUBLISHED, "Published")]

    title = models.CharField(max_length=220)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    featured_image = models.ForeignKey(
        ImageAsset, on_delete=models.SET_NULL, null=True, blank=True, related_name="research_featured"
    )
    description = models.TextField(blank=True)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default=DRAFT)
    pdf = models.FileField(upload_to="pdfs/", null=True, blank=True)  # optional

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)[:200]
            candidate = base
            i = 1
            while Research.objects.filter(slug=candidate).exclude(pk=self.pk).exists():
                i += 1
                candidate = f"{base}-{i}"
            self.slug = candidate
        super().save(*args, **kwargs)
