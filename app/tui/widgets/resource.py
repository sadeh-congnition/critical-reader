import traceback
from textual.screen import ModalScreen
from textual.app import ComposeResult
from django.core.exceptions import ValidationError
from textual.containers import Grid
from django.core.validators import URLValidator
from textual.widgets import Static, Input, Label, DataTable
from configuration.models import ProjectConfigRow

from tui.models import AppState
from tui.widgets.config import ConfigMissing
from common.models import ResourceRow
from common.jobs.job_dispatcher import Event, create_resource_processing_pipeline


class CreateResourceView(ModalScreen):
    BINDINGS = [
        ("escape", "app.pop_screen", "Close"),
    ]

    def compose(self) -> ComposeResult:
        yield Grid(
            Label("Enter URL", id="enter-url"),
            Input(placeholder="Enter URL", id="url-input"),
            id="new-resource",
        )

    async def on_input_submitted(self, event):
        val = URLValidator()
        try:
            val(event.value)
        except ValidationError:
            self.mount(Static("[red]Invalid URL[/]"))
            return

        project_config_row = await ProjectConfigRow.aget_by_project_id_for_ui(
            AppState.active_project_id
        )
        if not project_config_row:
            self.app.pop_screen()
            self.app.push_screen(ConfigMissing())
            return

        resource = await ResourceRow.acreate(AppState.active_project_id, event.value)
        project_config = await project_config_row.ato_obj()
        try:
            await create_resource_processing_pipeline(
                Event.RESOURCE_CREATED,
                project_config,
                AppState.active_project_id,
                resource.id,
            )
        except Exception:
            await resource.aadd_error(traceback.format_exc())
            raise
        self.app.pop_screen()


class ResroucesList(DataTable):
    def on_mount(self):
        self.add_columns("ID", "Name", "Status", "Error")

    async def make_rows(self, project_id_for_ui):
        resources = await ResourceRow.aget_all_by_project_id_for_ui(project_id_for_ui)
        for r in resources:
            if len(r.url) > 50:
                url = r.url[:50] + "..."
            else:
                url = r.url
            error_msg = r.error_msg.replace("\n", " ") if r.error_msg else ""
            self.add_row(r.id, url, r.status, error_msg)
