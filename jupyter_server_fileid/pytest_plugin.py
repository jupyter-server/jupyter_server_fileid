import os
from pathlib import Path

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


@pytest.fixture
def fs_helpers():
    class FsHelpers:
        # seconds after test start that the `touch` and `move` methods set
        # timestamps to
        fake_time = 1

        def touch(self, path, dir=False):
            """Creates a new file at `path`. The modified times of the file and
            its parent directory are guaranteed to be unique."""
            if dir:
                os.mkdir(path)
            else:
                Path(path).touch()

            parent = Path(path).parent
            stat = os.stat(path)
            current_time = stat.st_mtime + self.fake_time

            os.utime(parent, (stat.st_atime, current_time))
            os.utime(path, (current_time, current_time))

            self.fake_time += 1

        def move(self, old_path, new_path):
            """Moves a file from `old_path` to `new_path` while changing the modified
            timestamp of the parent directory accordingly. The modified time of the
            parent is guaranteed to be unique."""
            os.rename(old_path, new_path)
            parent = Path(new_path).parent
            stat = os.stat(parent)
            current_time = stat.st_mtime + self.fake_time

            os.utime(parent, (stat.st_atime, current_time))

            self.fake_time += 1

        def edit(self, path):
            """Simulates editing a file at `path` by updating its modified time
            accordingly.  The modified time of the file is guaranteed to be
            unique."""
            stat = os.stat(path)
            os.utime(path, (stat.st_atime, stat.st_mtime + self.fake_time))
            self.fake_time += 1

    return FsHelpers()
