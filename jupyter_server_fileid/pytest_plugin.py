import os

import pytest

from jupyter_server_fileid.manager import FileIdManager


@pytest.fixture
def jp_server_config(jp_server_config):
    return {"ServerApp": {"jpserver_extensions": {"jupyter_server_fileid": True}}}


@pytest.fixture
def fid_db_path(jp_data_dir):
    """Fixture that returns the file ID DB path used for tests."""
    return str(jp_data_dir / "fileidmanager_test.db")


@pytest.fixture(autouse=True)
def delete_fid_db(fid_db_path):
    """Fixture that automatically deletes the DB file after each test."""
    yield
    try:
        os.remove(fid_db_path)
    except OSError:
        pass


@pytest.fixture
def fid_manager(fid_db_path, jp_root_dir):
    """Fixture returning a test-configured instance of `FileIdManager`."""
    fid_manager = FileIdManager(db_path=fid_db_path, root_dir=str(jp_root_dir))
    # disable journal so no temp journal file is created under `tmp_path`.
    # reduces test flakiness since sometimes journal file has same ino and
    # crtime as a deleted file, so FID manager detects it wrongly as a move
    # also makes tests run faster :)
    fid_manager.con.execute("PRAGMA journal_mode = OFF")
    return fid_manager
