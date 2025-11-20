import os
import traceback
import requests

from django_async_job_pipelines.jobs import job

from common.models import ConversationConfigRow
from common.models import ResourceRow


@job(name="scrape_web_page_using_requests", timeout=10)
def scrape_web_page_using_requests(resource_id):
    try:
        resource: ResourceRow = ResourceRow.get_by_id(resource_id)
        resource.set_download_finishied()
        resource.set_scraping_finished()
        conversation_config_row = ConversationConfigRow.get_by_conversation_id_for_ui(
            resource.conversation.id_for_ui
        )
        assert conversation_config_row
        conversation_config = conversation_config_row.to_obj()
    except:
        resource.add_error(traceback.format_exc())
    return

    api_key = os.environ.get("JINA_AI_API_KEY")
    resource = ResourceRow.get_by_id(resource_id)
    resource.set_download_finishied()
    headers = {"Authorization": f"Bearer {api_key}"}
    resp = requests.get(f"https://r.jina.ai/{resource.url}", headers=headers)
    if resp.status_code == 200:
        resource.add_scraped_content(resp.text)
        resource.set_scraping_finished()
        return
    else:
        error_msg = (
            f"Error code from JINA API: {resp.status_code}\nError message: {resp.text}"
        )
        resource.add_error(error_msg)
