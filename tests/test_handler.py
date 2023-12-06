from unittest.mock import MagicMock

import pytest
from tornado.escape import json_decode
from tornado.httpclient import HTTPClientError

from jupyter_server_fileid.manager import BaseFileIdManager


class MockFileIdManager(BaseFileIdManager):
    _normalize_path = MagicMock()
    _from_normalized_path = MagicMock()
    index = MagicMock()
    move = MagicMock()
    copy = MagicMock()
    delete = MagicMock()
    save = MagicMock()
    get_handlers_by_action = MagicMock()
    get_path = MagicMock(return_value="mock_path")
    get_id = MagicMock(return_value="mock_id")


@pytest.fixture
def jp_server_config():
    yield {
        "ServerApp": {"jpserver_extensions": {"jupyter_server_fileid": True}},
        "FileIdExtension": {"file_id_manager_class": MockFileIdManager},
    }


@pytest.fixture
def file_id_extension(jp_serverapp):
    ext_pkg = jp_serverapp.extension_manager.extensions["jupyter_server_fileid"]
    ext_point = ext_pkg.extension_points["jupyter_server_fileid"]
    return ext_point.app


async def test_file_id_handler(jp_fetch, file_id_extension):
    response = await jp_fetch("api/fileid", params={"path": "test"})
    file_id_extension.file_id_manager.get_id.assert_called_once()
    body = json_decode(response.body)
    assert "id" in body
    assert body["id"] == "mock_id"

    response = await jp_fetch("api/fileid", params={"id": "test"})
    file_id_extension.file_id_manager.get_path.assert_called_once()
    body = json_decode(response.body)
    assert "path" in body
    assert body["path"] == "mock_path"


async def test_missing_query_parameters(jp_fetch):
    with pytest.raises(HTTPClientError) as err:
        response = await jp_fetch("api/fileid")

    assert err.value.code == 400


async def test_resource_not_found(jp_fetch, monkeypatch):
    def mock_get_id_with_exception(self, path):
        raise Exception("Not found.")

    monkeypatch.setattr(MockFileIdManager, "get_id", mock_get_id_with_exception)

    with pytest.raises(HTTPClientError) as err:
        response = await jp_fetch("api/fileid", params={"path": "test"})

    assert err.value.code == 404
