from django_async_job_pipelines.jobs import Job
from configuration.models import Config
from common.constants import Provider
from common.jobs.extract_text.using_apis.jina_ai_api import (
    scrape_web_page_using_requests,
)


def dispatcher(conversation_config: Config) -> Job:
    supported_extractors = [Provider.JINA]
    text_extractor = conversation_config.text_extractor

    if text_extractor.provider == Provider.JINA:
        return scrape_web_page_using_requests

    raise Exception(
        f"Unknown text extractor: [red]{text_extractor.provider}[/]\nSupported providers: {supported_extractors}"
    )
