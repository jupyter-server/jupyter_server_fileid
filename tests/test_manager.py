import ntpath
import os
import posixpath
import sys
from unittest.mock import patch

import pytest
from traitlets import TraitError

from jupyter_server_fileid.manager import (
    ArbitraryFileIdManager,
    BaseFileIdManager,
    LocalFileIdManager,
)


@pytest.fixture
def test_path(fs_helpers):
    path = "test_path"
    fs_helpers.touch(path, dir=True)
    return path


@pytest.fixture
def test_path_child(test_path, fs_helpers):
    path = os.path.join(test_path, "child")
    fs_helpers.touch(path)
    # return api-style path
    return posixpath.join(test_path, "child")


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
    # return api-style path
    return posixpath.join(old_path, "child")


@pytest.fixture
def old_path_grandchild(old_path_child, fs_helpers):
    path = os.path.join(old_path_child, "grandchild")
    fs_helpers.touch(path)
    # return api-style path
    return posixpath.join(old_path_child, "grandchild")


@pytest.fixture
def new_path():
    """Fixture for destination path for a FID manager move/copy operation"""
    return "new_path"


@pytest.fixture
def new_path_child(new_path):
    return posixpath.join(new_path, "child")


@pytest.fixture
def new_path_grandchild(new_path_child):
    return posixpath.join(new_path_child, "grandchild")


def _normalize_path_local(fid_manager, path):
    if os.path.commonprefix([fid_manager.root_dir, path]) != fid_manager.root_dir:
        path = os.path.join(fid_manager.root_dir, path)

    path = os.path.normcase(path)
    path = os.path.normpath(path)
    return path


def _normalize_separators(path):
    parts = path.strip("\\").split("\\")
    return "/".join(parts)


def _normalize_path_arbitrary(fid_manager, path):
    if posixpath.commonprefix([fid_manager.root_dir, path]) != fid_manager.root_dir:
        path = posixpath.join(fid_manager.root_dir, path)

    path = _normalize_separators(path)
    return path


def get_id_nosync(fid_manager, path):
    # We need to first put the path into a form the fileId manager implementation will for persistence.
    if isinstance(fid_manager, LocalFileIdManager):
        path = _normalize_path_local(fid_manager, path)
    else:
        path = _normalize_path_arbitrary(fid_manager, path)

    row = fid_manager.con.execute("SELECT id FROM Files WHERE path = ?", (path,)).fetchone()
    return row and row[0]


def get_path_nosync(fid_manager, id):
    row = fid_manager.con.execute("SELECT path FROM Files WHERE id = ?", (id,)).fetchone()
    path = row and row[0]

    if path is None:
        return None

    return os.path.relpath(path, os.path.normcase(fid_manager.root_dir))


def normalize_path(fid_manager: BaseFileIdManager, path: str) -> str:
    """Normalize path or case based on operating system and FileIdManager instance.

    When testing instances of LocalFileIdManager, we need to normalize the
    case relative to the OS when comparing results of get_path() since Windows
    is case-insensitive.

    When testing instances of ArbitraryFileIdManager, we need to normalize the
    path, regardless of OS, when comparing results of get_path() since this fileID
    manager must be filesystem agnostic.
    """
    if isinstance(fid_manager, LocalFileIdManager):
        path = os.path.normcase(path)

    parts = path.strip("\\").split("\\")
    return "/".join(parts)


def test_validates_root_dir(fid_db_path):
    root_dir = "s3://bucket"
    with pytest.raises(TraitError, match="must be an absolute path"):
        LocalFileIdManager(root_dir=root_dir, db_path=fid_db_path)
    # root_dir can be relative for ArbitraryFileIdManager instances (and None)
    afm = ArbitraryFileIdManager(root_dir=root_dir, db_path=fid_db_path)
    assert afm.root_dir == root_dir
    afm2 = ArbitraryFileIdManager(root_dir=None, db_path=fid_db_path)
    assert afm2.root_dir == ""


def test_validates_db_path(jp_root_dir, any_fid_manager_class):
    with pytest.raises(TraitError, match="must be an absolute path"):
        any_fid_manager_class(
            root_dir=str(jp_root_dir), db_path=os.path.join("some", "rel", "path")
        )


def test_different_roots(
    any_fid_manager_class, fid_db_path, jp_root_dir, test_path, test_path_child
):
    """Assert that default FIM implementations assign the same file the same
    file ID agnostic of contents manager root."""
    fid_manager_1 = any_fid_manager_class(db_path=fid_db_path, root_dir=str(jp_root_dir))
    fid_manager_2 = any_fid_manager_class(
        db_path=fid_db_path, root_dir=str(jp_root_dir / test_path)
    )

    id_1 = fid_manager_1.index(test_path_child)
    id_2 = fid_manager_2.index(os.path.basename(test_path_child))

    assert id_1 == id_2


def test_different_roots_arbitrary(fid_db_path):
    """Assert that ArbitraryFileIdManager assigns the same file the same file ID
    agnostic of contents manager root, even if non-local."""
    manager_1 = ArbitraryFileIdManager(db_path=fid_db_path, root_dir="s3://bucket")
    manager_2 = ArbitraryFileIdManager(db_path=fid_db_path, root_dir="s3://bucket/folder")

    id_1 = manager_1.index("folder/child")
    id_2 = manager_2.index("child")

    assert id_1 == id_2


def test_index(any_fid_manager, test_path):
    id = any_fid_manager.index(test_path)
    assert id is not None


def test_index_already_indexed(any_fid_manager, test_path):
    id = any_fid_manager.index(test_path)
    assert id == any_fid_manager.index(test_path)


@pytest.mark.skipif(
    sys.version_info < (3, 8) and sys.platform.startswith("win"),
    reason="symbolic links on Windows Python 3.7 not behaving like 3.8+",
)
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


crtime_support = os.name == "nt" or hasattr(os.stat_result, "st_birthtime")


@pytest.mark.skipif(not crtime_support, reason="Requires crtime support.")
def test_index_after_deleting_dir_in_same_path(fid_manager, test_path, fs_helpers):
    old_id = fid_manager.index(test_path)

    fs_helpers.delete(test_path)
    fs_helpers.touch(test_path, dir=True)
    new_id = fid_manager.index(test_path)

    assert old_id != new_id
    assert fid_manager.get_path(old_id) is None
    assert fid_manager.get_path(new_id) == test_path


@pytest.mark.skipif(not crtime_support, reason="Requires crtime support.")
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


def test_get_path_arbitrary_preserves_path(arbitrary_fid_manager):
    """Tests whether ArbitraryFileIdManager always preserves the file paths it
    receives."""
    path = "AbCd.txt"
    id = arbitrary_fid_manager.index(path)
    assert path == arbitrary_fid_manager.get_path(id)


def test_get_path_returns_api_path(jp_root_dir, fid_db_path):
    """Tests whether get_path() method always returns an API path, i.e. one
    relative to the server root and one delimited by forward slashes (even if
    os.path.sep = "\\")."""
    test_path = "a\\b\\c"
    expected_path = "a/b/c"
    manager = ArbitraryFileIdManager(
        root_dir=ntpath.join("c:", ntpath.normpath(str(jp_root_dir))), db_path=fid_db_path
    )

    id = manager.index(test_path)
    path = manager.get_path(id)
    assert path == expected_path


def test_optimistic_get_path(fid_manager, test_path, test_path_child):
    """_sync_all() should never be called in the best case, in which no paths
    were moved out-of-band."""
    with patch.object(fid_manager, "_sync_all") as mock:
        id_1 = fid_manager.index(test_path)
        id_2 = fid_manager.index(test_path_child)

        fid_manager.get_path(id_1)
        fid_manager.get_path(id_2)

        mock.assert_not_called()


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

    assert fid_manager.get_path(id) == normalize_path(fid_manager, new_test_path)


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

    assert fid_manager.get_path(id) == normalize_path(fid_manager, new_test_path)


def test_move_unindexed(any_fid_manager, old_path, new_path, fs_helpers):
    fs_helpers.move(old_path, new_path)
    id = any_fid_manager.move(old_path, new_path)

    assert id is not None
    assert any_fid_manager.get_id(old_path) is None
    assert any_fid_manager.get_id(new_path) == id
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
    any_fid_manager,
    old_path,
    old_path_child,
    old_path_grandchild,
    new_path,
    new_path_child,
    new_path_grandchild,
    fs_helpers,
):
    parent_id = any_fid_manager.index(old_path)
    child_id = any_fid_manager.index(old_path_child)
    grandchild_id = any_fid_manager.index(old_path_grandchild)

    fs_helpers.move(old_path, new_path)
    any_fid_manager.move(old_path, new_path)

    # we avoid using get_id() here as it auto-corrects wrong path updates via
    # its out-of-band move detection logic. too smart for its own good!
    assert get_id_nosync(any_fid_manager, new_path) == parent_id
    assert get_id_nosync(any_fid_manager, new_path_child) == child_id
    assert get_id_nosync(any_fid_manager, new_path_grandchild) == grandchild_id


def test_copy(any_fid_manager, old_path, new_path, fs_helpers):
    old_id = any_fid_manager.index(old_path)
    fs_helpers.copy(old_path, new_path)
    new_id = any_fid_manager.copy(old_path, new_path)

    assert old_id is not None
    assert new_id is not None
    assert old_id != new_id


def test_copy_recursive(
    any_fid_manager,
    old_path,
    old_path_child,
    old_path_grandchild,
    new_path,
    new_path_child,
    new_path_grandchild,
    fs_helpers,
):
    any_fid_manager.index(old_path)
    any_fid_manager.index(old_path_child)
    any_fid_manager.index(old_path_grandchild)

    fs_helpers.copy(old_path, new_path)
    any_fid_manager.copy(old_path, new_path)

    assert any_fid_manager.get_id(new_path) is not None
    assert any_fid_manager.get_id(new_path_child) is not None
    assert any_fid_manager.get_id(new_path_grandchild) is not None


def test_delete(any_fid_manager, test_path, fs_helpers):
    id = any_fid_manager.index(test_path)

    fs_helpers.delete(test_path)
    any_fid_manager.delete(test_path)

    assert any_fid_manager.get_id(test_path) is None
    assert any_fid_manager.get_path(id) is None


def test_delete_recursive(any_fid_manager, test_path, test_path_child, fs_helpers):
    any_fid_manager.index(test_path)
    any_fid_manager.index(test_path_child)

    fs_helpers.delete(test_path)
    any_fid_manager.delete(test_path)

    assert any_fid_manager.get_id(test_path_child) is None


def test_save(any_fid_manager, test_path, fs_helpers):
    id = any_fid_manager.index(test_path)

    fs_helpers.edit(test_path)
    any_fid_manager.save(test_path)

    assert any_fid_manager.get_id(test_path) == id


@pytest.mark.parametrize(
    "db_journal_mode", ["invalid", None, "DELETE", "TRUNCATE", "PERSIST", "MEMORY", "WAL", "OFF"]
)
def test_db_journal_mode(any_fid_manager_class, fid_db_path, jp_root_dir, db_journal_mode):
    if db_journal_mode == "invalid":  # test invalid
        with pytest.raises(TraitError, match=" must be one of "):
            any_fid_manager_class(
                db_path=fid_db_path, root_dir=str(jp_root_dir), db_journal_mode=db_journal_mode
            )
    else:
        if not db_journal_mode:  # test correct defaults
            expected_journal_mode = (
                "WAL" if any_fid_manager_class.__name__ == "LocalFileIdManager" else "DELETE"
            )
            fid_manager = any_fid_manager_class(db_path=fid_db_path, root_dir=str(jp_root_dir))
        else:  # test any valid value
            expected_journal_mode = db_journal_mode
            fid_manager = any_fid_manager_class(
                db_path=fid_db_path, root_dir=str(jp_root_dir), db_journal_mode=db_journal_mode
            )

        cursor = fid_manager.con.execute("PRAGMA journal_mode")
        actual_journal_mode = cursor.fetchone()
        assert actual_journal_mode[0].upper() == expected_journal_mode
