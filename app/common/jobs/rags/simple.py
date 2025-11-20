from django_async_job_pipelines.jobs import job
from common.models import Config, ResourceRow
from common.models import ConversationConfigRow, EventLogRows
from common.constants import EventTypes


@job(name="dummy rag", timeout=10)
def dummy_job(resource_id):
    resource = ResourceRow.get_by_id(id=resource_id)
    resource.set_processed()
    EventLogRows.create(
        resource.conversation.id, EventTypes.RESOURCE_PROCESSED, resource_id
    )


def rag_dispatcher(conversation_config: Config):
    return dummy_job
