from dataclasses import dataclass
from loguru import logger
from django_async_job_pipelines.jobs import Job
from django_async_job_pipelines.steps import Step

from common.constants import DownloaderType, Provider, ProcessorType, ChunkerType
from common.jobs.extract_text.job_dispatcher import (
    dispatcher as extract_text_dispatcher,
)
from common.jobs.rags.simple import rag_dispatcher
from common.models import ProjectRow
from configuration.models import Config


class Event:
    RESOURCE_CREATED = "resource_created"


@dataclass
class Planner:
    project_config: Config

    def download_job(self) -> Job | None:
        if (
            self.project_config.downloader.type
            == DownloaderType.JINA_AI_READER_USING_JINA_API
        ):
            return
        else:
            raise Exception(f"Unknown downloader: {self.project_config.downloader}")

    def text_extractor_job(self) -> Job | None:
        if self.project_config.text_extractor.provider == Provider.JINA:
            return extract_text_dispatcher(self.project_config)

    def rag_step_jobs(self):
        if self.project_config.processor.type == ProcessorType.SIMPLE_RAG:
            if self.project_config.processor.chunker.type == ChunkerType.NO_CHUNK:
                yield rag_dispatcher(self.project_config)
            else:
                raise Exception(
                    f"Unknown chunker: {self.project_config.processor.chunker}"
                )
        else:
            raise Exception(f"Unknown processor: {self.project_config.processor}")


async def create_resource_processing_pipeline(
    event, project_config: Config, project_id, resource_id
) -> Job:
    if event != Event.RESOURCE_CREATED:
        raise Exception("Unknown event")

    planner = Planner(project_config)

    download_job = planner.download_job()
    assert not download_job

    text_extract_step = Step()
    text_extract_job = planner.text_extractor_job()
    await text_extract_step.aadd_job(text_extract_job, project_id, resource_id)

    current_step = text_extract_step
    for jobs in planner.rag_step_jobs():
        next_step = await current_step.acreate_next_step()
        for j in jobs:
            await next_step.aadd_job(j, project_id, resource_id)

        current_step = next_step
