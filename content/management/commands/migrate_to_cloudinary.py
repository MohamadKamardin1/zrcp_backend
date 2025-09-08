import os
from django.core.management.base import BaseCommand
from django.conf import settings
from content.models import Blog, Research, ContentImage
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

        self.migrate_model_files(Blog, 'featured_image')
        self.migrate_model_files(Research, 'featured_image')
        self.migrate_model_files(Research, 'file')
        self.migrate_model_files(ContentImage, 'image')

        self.stdout.write(
            self.style.SUCCESS('Successfully migrated files to Cloudinary')
        )

    def migrate_model_files(self, model, field_name):
        self.stdout.write(f'Migrating {model.__name__}.{field_name}...')
        
        for instance in model.objects.all():
            field = getattr(instance, field_name)
            if field and field.name and not field.name.startswith('http'):
                try:
                    # Upload to Cloudinary
                    result = cloudinary.uploader.upload(
                        field.path,
                        public_id=f"{model.__name__.lower()}/{field.name}",
                        resource_type="auto"
                    )
                    
                    # Update the field with Cloudinary URL
                    setattr(instance, field_name, result['secure_url'])
                    instance.save()
                    
                    self.stdout.write(
                        f'  Migrated: {field.name} -> {result["secure_url"]}'
                    )
                    
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'  Error migrating {field.name}: {str(e)}')
                    )