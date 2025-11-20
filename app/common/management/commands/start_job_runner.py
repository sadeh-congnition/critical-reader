from django.core.management.base import BaseCommand
from django.core.management import call_command

from common.jobs.extract_text.using_apis.jina_ai_api import (
    scrape_web_page_using_requests,
)
from common.jobs.rags.simple import dummy_job


class Command(BaseCommand):
    def handle(self, *args, **options):
        call_command("start_consumer")
