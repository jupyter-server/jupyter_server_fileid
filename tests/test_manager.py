import os
from unittest.mock import patch

import pytest
from traitlets import TraitError

from jupyter_server_fileid.manager import ArbitraryFileIdManager, LocalFileIdManager


@pytest.fixture
def test_path(fs_helpers):
    path = "test_path"
    fs_helpers.touch(path, dir=True)
    return path


@pytest.fixture
def test_path_child(test_path, fs_helpers):
    path = os.path.join(test_path, "child")
    fs_helpers.touch(path)
    return path


@pytest.fixture
def old_path(fs_helpers):
    """Fixture for source path to be moved/copied via FID manager"""
    path = "old_path"
    fs_helpers.touch(path, dir=True)
    return path


@pytest.fixture
def old_path_child(old_path, fs_helpers):
    path = os.path.join(old_path, "child")
    fs_helpers.touch(path, dir=True)
    return path


@pytest.fixture
def old_path_grandchild(old_path_child, fs_helpers):
    path = os.path.join(old_path_child, "grandchild")
    fs_helpers.touch(path)
    return path


@pytest.fixture
def new_path():
    """Fixture for destination path for a FID manager move/copy operation"""
    return "new_path"


@pytest.fixture
def new_path_child(new_path):
    return os.path.join(new_path, "child")


@pytest.fixture
def new_path_grandchild(new_path_child):
    return os.path.join(new_path_child, "grandchild")


def get_id_nosync(fid_manager, path):
    if not os.path.isabs(path):
        path = os.path.join(fid_manager.root_dir, path)

    row = fid_manager.con.execute("SELECT id FROM Files WHERE path = ?", (path,)).fetchone()
    return row and row[0]


def get_path_nosync(fid_manager, id):
    row = fid_manager.con.execute("SELECT path FROM Files WHERE id = ?", (id,)).fetchone()
    path = row and row[0]

    if path is None:
        return None

    return os.path.relpath(path, fid_manager.root_dir)


def test_validates_root_dir(fid_db_path):
    with pytest.raises(TraitError, match="must be an absolute path"):
        LocalFileIdManager(root_dir=os.path.join("some", "rel", "path"), db_path=fid_db_path)
    with pytest.raises(TraitError, match="must be an absolute path"):
        ArbitraryFileIdManager(root_dir=os.path.join("some", "rel", "path"), db_path=fid_db_path)


def test_validates_db_path(jp_root_dir):
    with pytest.raises(TraitError, match="must be an absolute path"):
        LocalFileIdManager(root_dir=str(jp_root_dir), db_path=os.path.join("some", "rel", "path"))
    with pytest.raises(TraitError, match="must be an absolute path"):
        ArbitraryFileIdManager(
            root_dir=str(jp_root_dir), db_path=os.path.join("some", "rel", "path")
        )


def test_index(any_fid_manager, test_path):
    id = any_fid_manager.index(test_path)
    assert id is not None


def test_index_already_indexed(any_fid_manager, test_path):
    id = any_fid_manager.index(test_path)
    assert id == any_fid_manager.index(test_path)


def test_index_symlink(fid_manager, test_path):
    link_path = os.path.join(fid_manager.root_dir, "link_path")
    os.symlink(os.path.join(fid_manager.root_dir, test_path), link_path)
    id = fid_manager.index(link_path)

    # we want to assert that the "real path" is the only path associated with an
    # ID. get_path() *sometimes* returns the real path if _sync_file() happens
    # to be called on the real path after the symlink path when _sync_all() is
    # run, causing this test to flakily pass when it shouldn't.
    assert get_path_nosync(fid_manager, id) == test_path


# test out-of-band move detection for FIM.index()
def test_index_oob_move(fid_manager, old_path, new_path, fs_helpers):
    id = fid_manager.index(old_path)
    fs_helpers.move(old_path, new_path)
    assert fid_manager.index(new_path) == id


def test_index_after_deleting_dir_in_same_path(fid_manager, test_path, fs_helpers):
    old_id = fid_manager.index(test_path)

    fs_helpers.delete(test_path)
    fs_helpers.touch(test_path, dir=True)
    new_id = fid_manager.index(test_path)

    assert old_id != new_id
    assert fid_manager.get_path(old_id) is None
    assert fid_manager.get_path(new_id) == test_path


def test_index_after_deleting_regfile_in_same_path(fid_manager, test_path_child, fs_helpers):
    old_id = fid_manager.index(test_path_child)

    fs_helpers.delete(test_path_child)
    fs_helpers.touch(test_path_child)
    new_id = fid_manager.index(test_path_child)

    assert old_id != new_id
    assert fid_manager.get_path(old_id) is None
    assert fid_manager.get_path(new_id) == test_path_child


@pytest.fixture
def stub_stat_crtime(fid_manager, request):
    """Fixture that stubs the _stat() method on fid_manager to always return a
    StatStruct with a fixed crtime."""
    if hasattr(request, "param") and not request.param:
        return False

    stat_real = fid_manager._stat

    def stat_stub(path):
        stat = stat_real(path)
        if stat:
            stat.crtime = 123456789
        return stat

    fid_manager._stat = stat_stub
    return True


# sync file should work even after directory mtime changes when children are
# added/removed/renamed on platforms supporting crtime
def test_index_crtime(fid_manager, test_path, stub_stat_crtime):
    abs_path = os.path.join(fid_manager.root_dir, test_path)
    stat = os.stat(abs_path)
    id = fid_manager.index(test_path)
    os.utime(abs_path, ns=(stat.st_atime_ns, stat.st_mtime_ns + 1000))

    assert fid_manager.index(test_path) == id


def test_getters_indexed(any_fid_manager, test_path):
    id = any_fid_manager.index(test_path)

    assert any_fid_manager.get_id(test_path) == id
    assert any_fid_manager.get_path(id) == test_path


def test_getters_nonnormalized(fid_manager, test_path, fs_helpers):
    path1 = os.path.join(test_path, "file")
    path2 = os.path.join(test_path, "some_dir", "..", "file")
    path3 = os.path.join(test_path, ".", ".", ".", "file")
    fs_helpers.touch(path1)

    id = fid_manager.index(path1)

    assert fid_manager.get_id(path1) == id
    assert fid_manager.get_id(path2) == id
    assert fid_manager.get_id(path3) == id


def test_getters_oob_delete(fid_manager, test_path, fs_helpers):
    id = fid_manager.index(test_path)
    fs_helpers.delete(test_path)
    assert id is not None
    assert fid_manager.get_id(test_path) is None
    assert fid_manager.get_path(id) is None


def test_get_id_unindexed(any_fid_manager, test_path_child):
    assert any_fid_manager.get_id(test_path_child) is None


# test out-of-band move detection for FIM.get_id()
def test_get_id_oob_move(fid_manager, old_path, new_path, fs_helpers):
    id = fid_manager.index(old_path)
    fs_helpers.move(old_path, new_path)
    assert fid_manager.get_id(new_path) == id


def test_get_id_oob_move_recursive(
    fid_manager, old_path, old_path_child, new_path, new_path_child, fs_helpers
):
    parent_id = fid_manager.index(old_path)
    child_id = fid_manager.index(old_path_child)

    fs_helpers.move(old_path, new_path)

    assert fid_manager.get_id(new_path) == parent_id
    assert fid_manager.get_id(new_path_child) == child_id


# make sure that out-of-band moves are detected even when a new file is created
# at the old path.  this is what forces relaxation of the UNIQUE constraint on
# path column, since we need to keep records of deleted files that used to
# occupy a path, which is possibly occupied by a new file.
def test_get_id_oob_move_new_file_at_old_path(fid_manager, old_path, new_path, fs_helpers):
    old_id = fid_manager.index(old_path)
    other_path = "other_path"

    fs_helpers.move(old_path, new_path)
    fs_helpers.touch(old_path)
    other_id = fid_manager.index(old_path)
    fs_helpers.move(old_path, other_path)

    assert other_id != old_id
    assert fid_manager.get_id(new_path) == old_id
    assert fid_manager.get_path(old_id) == new_path
    assert fid_manager.get_id(other_path) == other_id


def test_get_path_oob_move(fid_manager, old_path, new_path, fs_helpers):
    id = fid_manager.index(old_path)
    fs_helpers.move(old_path, new_path)
    assert fid_manager.get_path(id) == new_path


def test_get_path_oob_move_recursive(
    fid_manager, old_path, old_path_child, new_path, new_path_child, fs_helpers
):
    id = fid_manager.index(old_path)
    child_id = fid_manager.index(old_path_child)

    fs_helpers.move(old_path, new_path)

    assert fid_manager.get_path(id) == new_path
    assert fid_manager.get_path(child_id) == new_path_child


def test_get_path_oob_move_into_unindexed(
    fid_manager, old_path, old_path_child, new_path, new_path_child, fs_helpers
):
    fid_manager.index(old_path)
    id = fid_manager.index(old_path_child)

    fs_helpers.touch(new_path, dir=True)
    fs_helpers.move(old_path_child, new_path_child)

    assert fid_manager.get_path(id) == new_path_child


def test_get_path_oob_move_back_to_original_path(fid_manager, old_path, new_path, fs_helpers):
    id = fid_manager.index(old_path)
    fs_helpers.move(old_path, new_path)

    assert fid_manager.get_path(id) == new_path
    fs_helpers.move(new_path, old_path)
    fid_manager.sync_all()
    assert fid_manager.get_path(id) == old_path


# move file into an indexed-but-moved directory
# this test should work regardless of whether crtime is supported on platform
@pytest.mark.parametrize("stub_stat_crtime", [True, False], indirect=["stub_stat_crtime"])
def test_get_path_oob_move_nested(fid_manager, old_path, new_path, stub_stat_crtime, fs_helpers):
    old_test_path = "test_path"
    new_test_path = os.path.join(new_path, "test_path")
    fs_helpers.touch(old_test_path)
    fid_manager.index(old_path)
    id = fid_manager.index(old_test_path)

    fs_helpers.move(old_path, new_path)
    fs_helpers.move(old_test_path, new_test_path)

    assert fid_manager.get_path(id) == new_test_path


# move file into directory within an indexed-but-moved directory
# this test should work regardless of whether crtime is supported on platform
@pytest.mark.parametrize("stub_stat_crtime", [True, False], indirect=["stub_stat_crtime"])
def test_get_path_oob_move_deeply_nested(
    fid_manager, old_path, new_path, old_path_child, new_path_child, stub_stat_crtime, fs_helpers
):
    old_test_path = "test_path"
    new_test_path = os.path.join(new_path_child, "test_path")
    fs_helpers.touch(old_test_path)
    fid_manager.index(old_path)
    fid_manager.index(old_path_child)
    id = fid_manager.index(old_test_path)

    fs_helpers.move(old_path, new_path)
    fs_helpers.move(old_test_path, new_test_path)

    assert fid_manager.get_path(id) == new_test_path


def test_move_unindexed(any_fid_manager, old_path, new_path, fs_helpers):
    fs_helpers.move(old_path, new_path)
    id = any_fid_manager.move(old_path, new_path)

    assert id is not None
    assert any_fid_manager.get_id(old_path) is None
    assert any_fid_manager.get_id(new_path) is id
    assert any_fid_manager.get_path(id) == new_path


def test_move_indexed(any_fid_manager, old_path, new_path, fs_helpers):
    old_id = any_fid_manager.index(old_path)

    fs_helpers.move(old_path, new_path)
    new_id = any_fid_manager.move(old_path, new_path)

    assert old_id == new_id
    assert any_fid_manager.get_id(old_path) is None
    assert any_fid_manager.get_id(new_path) == new_id
    assert any_fid_manager.get_path(old_id) == new_path


# test for disjoint move handling
# disjoint move: any out-of-band move that does not preserve stat info
def test_disjoint_move_indexed(any_fid_manager, old_path, new_path, fs_helpers):
    old_id = any_fid_manager.index(old_path)

    fs_helpers.delete(old_path)
    fs_helpers.touch(new_path, dir=True)
    new_id = any_fid_manager.move(old_path, new_path)

    assert old_id == new_id


def test_move_recursive(
    fid_manager,
    old_path,
    old_path_child,
    old_path_grandchild,
    new_path,
    new_path_child,
    new_path_grandchild,
    fs_helpers,
):
    parent_id = fid_manager.index(old_path)
    child_id = fid_manager.index(old_path_child)
    grandchild_id = fid_manager.index(old_path_grandchild)

    fs_helpers.move(old_path, new_path)
    fid_manager.move(old_path, new_path)

    # we avoid using get_id() here as it auto-corrects wrong path updates via
    # its out-of-band move detection logic. too smart for its own good!
    assert get_id_nosync(fid_manager, new_path) == parent_id
    assert get_id_nosync(fid_manager, new_path_child) == child_id
    assert get_id_nosync(fid_manager, new_path_grandchild) == grandchild_id


def test_copy(any_fid_manager, old_path, new_path, fs_helpers):
    old_id = any_fid_manager.index(old_path)
    fs_helpers.copy(old_path, new_path)
    new_id = any_fid_manager.copy(old_path, new_path)

    assert old_id is not None
    assert new_id is not None
    assert old_id != new_id


def test_copy_recursive(
    fid_manager,
    old_path,
    old_path_child,
    old_path_grandchild,
    new_path,
    new_path_child,
    new_path_grandchild,
    fs_helpers,
):
    fid_manager.index(old_path)
    fid_manager.index(old_path_child)
    fid_manager.index(old_path_grandchild)

    fs_helpers.copy(old_path, new_path)
    fid_manager.copy(old_path, new_path)

    assert fid_manager.get_id(new_path) is not None
    assert fid_manager.get_id(new_path_child) is not None
    assert fid_manager.get_id(new_path_grandchild) is not None


def test_delete(any_fid_manager, test_path, fs_helpers):
    id = any_fid_manager.index(test_path)

    fs_helpers.delete(test_path)
    any_fid_manager.delete(test_path)

    assert any_fid_manager.get_id(test_path) is None
    assert any_fid_manager.get_path(id) is None


def test_delete_recursive(fid_manager, test_path, test_path_child, fs_helpers):
    fid_manager.index(test_path)
    fid_manager.index(test_path_child)

    fs_helpers.delete(test_path)
    fid_manager.delete(test_path)

    assert fid_manager.get_id(test_path_child) is None


def test_save(any_fid_manager, test_path, fs_helpers):
    id = any_fid_manager.index(test_path)

    fs_helpers.edit(test_path)
    any_fid_manager.save(test_path)

    assert any_fid_manager.get_id(test_path) == id


def test_autosync_gt_0(fid_manager, old_path, new_path, fs_helpers):
    fid_manager.autosync_interval = 10
    id = fid_manager.index(old_path)
    fid_manager.sync_all()
    fs_helpers.move(old_path, new_path)

    assert fid_manager.get_path(id) != new_path
    with patch("time.time") as mock_time:
        mock_time.return_value = fid_manager._last_sync + 999
        assert fid_manager.get_path(id) == new_path


def test_autosync_eq_0(fid_manager, old_path, new_path, fs_helpers):
    fid_manager.autosync_interval = 0
    id = fid_manager.index(old_path)
    fid_manager.sync_all()
    fs_helpers.move(old_path, new_path)

    assert fid_manager.get_path(id) == new_path


def test_autosync_lt_0(fid_manager, old_path, new_path, fs_helpers):
    fid_manager.autosync_interval = -10
    id = fid_manager.index(old_path)
    fid_manager.sync_all()
    fs_helpers.move(old_path, new_path)

    assert fid_manager.get_path(id) != new_path
    with patch("time.time") as mock_time:
        mock_time.return_value = fid_manager._last_sync + 999
        assert fid_manager.get_path(id) != new_path

    fid_manager.sync_all()
    assert fid_manager.get_path(id) == new_path
