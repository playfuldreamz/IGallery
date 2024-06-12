from django.db import models
from django.conf import settings
from django.core.cache import cache
import json

class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    instagram_access_token = models.CharField(max_length=255, blank=True, null=True)
    saved_photos_data = models.TextField(blank=True, null=True)
    saved_image_urls = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    def get_cached_image_urls(self):
        """Retrieves image URLs, utilizing caching for efficiency."""
        cache_key = f"saved_image_urls_{self.id}" 
        cached_urls = cache.get(cache_key)

        if cached_urls:
            return cached_urls 

        # Not in cache, extract, cache, and return:
        image_urls = self.extract_image_urls()
        cache.set(cache_key, image_urls) 
        return image_urls
    
    def extract_image_urls(self):
        """
        Parses the saved_photos_data JSON and extracts image URLs.
        """
        if not self.saved_photos_data:
            return []

        data = json.loads(self.saved_photos_data)
        image_urls = []
        for item in data.get('saved_saved_media', []):
            post_url = item.get('string_map_data', {}).get('Saved on', {}).get('href')
            if post_url:
                image_urls.append(post_url)
        return image_urls