import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify

User = get_user_model()

def upload_to(instance, filename):
    """
    Generate unique filenames for uploads based on model type.
    """
    ext = filename.split('.')[-1].lower()
    unique_filename = f"{uuid.uuid4().hex}.{ext}"

    if hasattr(instance, 'blog_post'):
        return f"blog/{unique_filename}"
    elif hasattr(instance, 'research'):
        return f"research/{unique_filename}"
    elif isinstance(instance, Blog):
        return f"blog/featured/{unique_filename}"
    elif isinstance(instance, Research):
        return f"research/featured/{unique_filename}"
    else:
        return f"misc/{unique_filename}"


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class ImageAsset(TimeStampedModel):
    """Reusable image (for blog inline images or research banners)."""
    file = models.ImageField(upload_to=upload_to)
    alt_text = models.CharField(max_length=255, blank=True, default="")

    def __str__(self):
        return self.alt_text or self.file.name


class ContentBase(TimeStampedModel):
    """Abstract base for content with featured image and slug."""
    title = models.CharField(max_length=220)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    featured_image = models.ImageField(upload_to=upload_to, blank=True, null=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)[:200]
            candidate = base
            i = 1
            while self.__class__.objects.filter(slug=candidate).exclude(pk=self.pk).exists():
                i += 1
                candidate = f"{base}-{i}"
            self.slug = candidate
        super().save(*args, **kwargs)


class Blog(ContentBase):
    DRAFT = "draft"
    PUBLISHED = "published"
    STATUS_CHOICES = [(DRAFT, "Draft"), (PUBLISHED, "Published")]

    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    summary = models.TextField(blank=True, help_text="Short excerpt for listings/SEO")
    body = models.JSONField(default=list, blank=True)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default=DRAFT)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-published_at", "-created_at"]

    def __str__(self):
        return self.title


class Research(ContentBase):
    DRAFT = "draft"
    IN_REVIEW = "in_review"
    PUBLISHED = "published"
    STATUS_CHOICES = [(DRAFT, "Draft"), (IN_REVIEW, "In Review"), (PUBLISHED, "Published")]

    description = models.TextField(blank=True)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default=DRAFT)
    file = models.FileField(upload_to=upload_to, blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class ContentImage(TimeStampedModel):
    """Inline image used in content blocks."""
    image = models.ImageField(upload_to=upload_to, blank=True, null=True)
    alt_text = models.CharField(max_length=255, blank=True, default="")

    def __str__(self):
        return self.alt_text or self.image.name
