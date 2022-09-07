from jupyter_server.extension.application import ExtensionApp
from traitlets import Type, default

from jupyter_server_fileid.manager import FileIdManager


class FileIdExtension(ExtensionApp):

    name = "jupyter_server_fileid"

    file_id_manager_class = Type(
        klass=FileIdManager,
        help="File ID manager instance to use. Defaults to FileIdManager.",
        config=True,
    )

    @default("file_id_manager")
    def _file_id_manager_default(self):
        self.log.debug("No File ID manager configured. Defaulting to FileIdManager")
        return FileIdManager

    def initialize_settings(self):
        self.log.debug("Configured File ID manager: %s" % self.file_id_manager_class.__name__)
        file_id_manager = self.file_id_manager_class(log=self.log, root_dir=self.serverapp.root_dir)
        self.settings.update({"file_id_manager": file_id_manager})
