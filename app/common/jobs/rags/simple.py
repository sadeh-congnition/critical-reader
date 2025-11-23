from configuration.models import Config
from django_async_job_pipelines.jobs import job

from common.constants import EventTypes
from common.models import EventLogRows, ResourceRow


@job(name="dummy rag", timeout=10)
def dummy_rag(conversation_id, resource_id):
    resource = ResourceRow.get_by_id(id=resource_id)

    if not resource:
        EventLogRows.create(
            conversation_id,
            EventTypes.RESOURCE_PROCESSING_ENCOUNTERED_ERROR,
            resource_id,
        )
        return

    resource.set_processed()
    EventLogRows.create(
        resource.conversation.id, EventTypes.RESOURCE_PROCESSED, resource_id
    )


def rag_dispatcher(conversation_config: Config):
    return [dummy_rag]
