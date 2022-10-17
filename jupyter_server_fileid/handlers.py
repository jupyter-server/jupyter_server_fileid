from jupyter_server.auth import authorized
from jupyter_server.base.handlers import APIHandler
from tornado import web

AUTH_RESOURCE = "contents"


class FileIdAPIHandler(APIHandler):
    auth_resource = AUTH_RESOURCE


class FilePath2IdHandler(FileIdAPIHandler):
    @web.authenticated
    @authorized
    async def get(self, path):
        manager = self.settings["file_id_manager"]

        idx = manager.get_id(path)
        if idx is None:
            # index does not exist
            raise web.HTTPError(404, f"No ID found for file {path!r}")

        # index exists, return it
        return self.finish(str(idx))

    @web.authenticated
    @authorized
    async def put(self, path):
        manager = self.settings["file_id_manager"]

        idx = manager.get_id(path)
        if idx is not None:
            # index already exists
            self.set_status(200)
            return self.finish(str(idx))

        # try indexing
        idx = manager.index(path)
        if idx is None:
            # file does not exists
            raise web.HTTPError(404, f"File {path!r} does not exist")

        # index successfully created
        self.set_status(201)
        return self.finish(str(idx))


class FileId2PathHandler(FileIdAPIHandler):
    @web.authenticated
    @authorized
    async def get(self, idx):
        manager = self.settings["file_id_manager"]

        path = manager.get_path(idx)

        if path is None:
            raise web.HTTPError(404, f"No path found for ID {idx!r}")

        return self.finish(str(path))

    @web.authenticated
    @authorized
    async def put(self, idx):
        raise web.HTTPError(501, "Cannot set a file's ID")
