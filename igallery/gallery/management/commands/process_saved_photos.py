import json
import asyncio
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from gallery.models import UserProfile
from playwright.async_api import async_playwright
from django.core.files.uploadedfile import InMemoryUploadedFile

class Command(BaseCommand):
    help = "Processes uploaded saved Instagram photos JSON data."

    def add_arguments(self, parser):
        parser.add_argument('user_id', type=int, help='ID of the user to process data for.')
        parser.add_argument('--dummy', action='store_true', help='Dummy argument (not used)')

    async def extract_image_url(self, post_url):
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.goto(post_url)
            image_element = await page.query_selector('div._aagv > img')
            image_url = await image_element.get_attribute('src') if image_element else None
            await browser.close()
            return image_url

    def handle(self, *args, **options):
        user_id = options['user_id']

        try:
            user_profile = UserProfile.objects.get(user_id=user_id)
        except UserProfile.DoesNotExist:
            self.stderr.write(self.style.ERROR(f"User with ID {user_id} not found."))
            return

        json_data = json.loads(user_profile.saved_photos_data)
        user_profile.saved_photos_data = json.dumps(json_data)
        user_profile.save()

        # Run the async part synchronously
        extracted_url_count = asyncio.run(self.extract_and_cache_urls(user_profile))

        self.stdout.write(self.style.SUCCESS("Successfully processed saved photos data!"))
        self.stdout.write(self.style.SUCCESS(f"Extracted and cached {extracted_url_count} image URLs."))

    async def extract_and_cache_urls(self, user_profile):
        image_urls = []
        for post_url in user_profile.extract_image_urls():
            image_url = await self.extract_image_url(post_url)
            image_urls.append(image_url)
        user_profile.saved_image_urls = json.dumps(image_urls)
        user_profile.save()
        return len(image_urls)
