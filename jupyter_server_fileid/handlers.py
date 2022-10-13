from tornado import web

from jupyter_server.auth import authorized
from jupyter_server.base.handlers import APIHandler


AUTH_RESOURCE = "contents"

class FileIdAPIHandler(APIHandler):
    auth_resource = AUTH_RESOURCE


class FileIdHandler(FileIdAPIHandler):

    @web.authenticated
    @authorized
    async def get(self, path):
        idx = self.settings["file_id_manager"].index(path)

        if idx is None:
            raise web.HTTPError(404, f"File {path!r} does not exist")

        return self.finish(str(idx))
