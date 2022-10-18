from jupyter_events.logger import EventLogger
from jupyter_server.extension.application import ExtensionApp
from traitlets import Type, default

from jupyter_server_fileid.manager import FileIdManager

from .handlers import FileId2PathHandler, FilePath2IdHandler


class FileIdExtension(ExtensionApp):

    name = "jupyter_server_fileid"

    file_id_manager_class = Type(
        klass=FileIdManager,
        help="File ID manager instance to use. Defaults to FileIdManager.",
        config=True,
    )

    @default("file_id_manager")
    def _file_id_manager_default(self):
        self.log.debug("No File ID manager configured. Defaulting to FileIdManager.")
        return FileIdManager

    def initialize_settings(self):
        self.log.debug(f"Configured File ID manager: {self.file_id_manager_class.__name__}")
        file_id_manager = self.file_id_manager_class(log=self.log, root_dir=self.serverapp.root_dir)
        self.settings.update({"file_id_manager": file_id_manager})

        # attach listener to contents manager events (requires jupyter_server~=2)
        if "event_logger" in self.settings:
            self.initialize_event_listeners()

    def initialize_event_listeners(self):
        file_id_manager = self.settings["file_id_manager"]

        # define event handlers per contents manager action
        handlers_by_action = {
            "get": None,
            "save": lambda data: file_id_manager.save(data["path"]),
            "rename": lambda data: file_id_manager.move(data["source_path"], data["path"]),
            "copy": lambda data: file_id_manager.copy(data["source_path"], data["path"]),
            "delete": lambda data: file_id_manager.delete(data["path"]),
        }

        async def cm_listener(logger: EventLogger, schema_id: str, data: dict) -> None:
            handler = handlers_by_action[data["action"]]
            if handler:
                handler(data)

        self.settings["event_logger"].add_listener(
            schema_id="https://events.jupyter.org/jupyter_server/contents_service/v1",
            listener=cm_listener,
        )
        self.log.info("Attached event listeners.")

    def initialize_handlers(self):
        self.handlers.extend(
            [
                (
                    r"/api/fileid/id/(.*)",
                    FilePath2IdHandler,
                ),
                (
                    r"/api/fileid/path/(.*)",
                    FileId2PathHandler,
                ),
            ],
        )
