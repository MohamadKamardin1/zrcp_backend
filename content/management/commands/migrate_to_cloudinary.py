import os
from django.core.management.base import BaseCommand
from django.conf import settings
from content.models import Blog, Research, ContentImage, ImageAsset
import cloudinary
import cloudinary.uploader
from pathlib import Path

class Command(BaseCommand):
    help = 'Migrate local media files to Cloudinary'

    def handle(self, *args, **options):
        # Configure Cloudinary
        cloudinary.config(
            cloud_name=settings.CLOUDINARY_STORAGE['CLOUD_NAME'],
            api_key=settings.CLOUDINARY_STORAGE['API_KEY'],
            api_secret=settings.CLOUDINARY_STORAGE['API_SECRET']
        )

        self.migrate_related_image(Blog, 'featured_image')
        self.migrate_related_image(Research, 'featured_image')
        self.migrate_direct_file(Research, 'file')
        self.migrate_direct_file(ContentImage, 'image')

        self.stdout.write(
            self.style.SUCCESS('✅ Successfully migrated files to Cloudinary')
        )

    def migrate_related_image(self, model, field_name):
        """Handles ForeignKey to ImageAsset"""
        self.stdout.write(f'🔄 Migrating {model.__name__}.{field_name} (ImageAsset)...')

        for instance in model.objects.select_related(field_name).all():
            image_asset = getattr(instance, field_name)
            if image_asset and image_asset.file and image_asset.file.name and not image_asset.file.url.startswith('http'):
                try:
                    result = cloudinary.uploader.upload(
                        image_asset.file.path,
                        public_id=f"{model.__name__.lower()}/{image_asset.file.name}",
                        resource_type="image"
                    )
                    # image_asset.file = result['secure_url']
                    from django.core.files.base import ContentFile
                    import requests

                    response = requests.get(result['secure_url'])
                    image_asset.file.save(image_asset.file.name, ContentFile(response.content), save=True)
                    image_asset.save()

                    self.stdout.write(f'  ✅ Migrated: {image_asset.file.name} -> {result["secure_url"]}')
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'  ❌ Error migrating {image_asset.file.name}: {str(e)}'))

    def migrate_direct_file(self, model, field_name):
        """Handles direct FileField or ImageField"""
        self.stdout.write(f'🔄 Migrating {model.__name__}.{field_name} (FileField)...')

        for instance in model.objects.all():
            file_field = getattr(instance, field_name)
            if file_field and file_field.name and not file_field.url.startswith('http'):
                try:
                    result = cloudinary.uploader.upload(
                        file_field.path,
                        public_id=f"{model.__name__.lower()}/{file_field.name}",
                        resource_type="auto"
                    )
                    setattr(instance, field_name, result['secure_url'])
                    instance.save()

                    self.stdout.write(f'  ✅ Migrated: {file_field.name} -> {result["secure_url"]}')
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'  ❌ Error migrating {file_field.name}: {str(e)}'))
