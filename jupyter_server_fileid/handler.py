from jupyter_server.auth.decorator import authorized
from jupyter_server.base.handlers import APIHandler
from jupyter_server.extension.handler import ExtensionHandlerMixin
from tornado import web
from tornado.escape import json_encode

from .manager import BaseFileIdManager


class FileIDHandler(ExtensionHandlerMixin, APIHandler):
    """Preovides a simple REST API for fetching the File ID information of a file."""

    auth_resource = "contents"

    @property
    def file_id_manager(self) -> BaseFileIdManager:
        return self.settings.get("file_id_manager")

    @web.authenticated
    @authorized
    def get(self):
        path: str = self.get_argument("path", None)
        id: str = self.get_argument("id", None)
        response = {"id": id, "path": path}
        # If no query parameter is given, log a helpful message.
        if not path and not id:
            raise web.HTTPError(
                400, log_message="No 'id' or 'path' parameters were provided in the request."
            )
        needed_index, known_value = ("id", path) if path else ("path", id)
        try:
            index_method = getattr(self.file_id_manager, f"get_{needed_index}")
            response[needed_index] = index_method(known_value)
            self.write(json_encode(response))
        except Exception as err:
            raise web.HTTPError(
                404,
                log_message=str(err),
                reason=f"The {needed_index} for file, {known_value}, could not be found.",
            )
