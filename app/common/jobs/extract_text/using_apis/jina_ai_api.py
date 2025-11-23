import os
import traceback
import requests

from django_async_job_pipelines.jobs import job

from configuration.models import ProjectConfigRow
from common.models import ResourceRow, EventLogRows
from common.constants import EventTypes


@job(name="scrape_web_page_using_requests", timeout=10)
def scrape_web_page_using_requests(project_config, resource_id):
    resource: ResourceRow | None = ResourceRow.get_by_id(resource_id)

    if not resource:
        EventLogRows.create(
            project_id=project_config.project_id,
            type=EventTypes.RESOURCE_PROCESSING_ENCOUNTERED_ERROR,
            entity_id=resource_id,
        )
        return

    try:
        EventLogRows.create(
            resource.project.id,
            EventTypes.RESOURCE_PROCESSING_STARTED,
            resource_id,
        )

        resource.set_download_finishied()

        project_row = ProjectConfigRow.get_by_project_id_for_ui(
            resource.project.id_for_ui
        )
        assert project_row

        api_key = os.environ.get("JINA_AI_API_KEY")
        resource.set_download_finishied()
        headers = {"Authorization": f"Bearer {api_key}"}
        resp = requests.get(f"https://r.jina.ai/{resource.url}", headers=headers)
        if resp.status_code == 200:
            resource.add_scraped_content(resp.text)
            resource.set_scraping_finished()
            EventLogRows.create(
                resource.project.id,
                EventTypes.RESOURCE_DOWNLOADED_AND_TEXT_EXTRACTED,
                resource_id,
            )
            return
        else:
            error_msg = f"Error code from JINA API: {resp.status_code}\nError message: {resp.text}"
            resource.add_error(error_msg)
            EventLogRows.create(
                resource.project.id,
                EventTypes.RESOURCE_PROCESSING_ENCOUNTERED_ERROR,
                resource_id,
            )
    except:
        resource.add_error(traceback.format_exc())
        EventLogRows.create(
            resource.project.id,
            EventTypes.RESOURCE_PROCESSING_ENCOUNTERED_ERROR,
            resource_id,
        )
        return
