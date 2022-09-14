"""A Jupyter Server extension providing an implementation of the File ID service."""
from .extension import FileIdExtension

version_info = (0, 2, 0, "", "")
__version__ = ".".join(map(str, version_info[:3])) + "".join(version_info[3:])


def _jupyter_server_extension_points():
    return [{"module": "jupyter_server_fileid", "app": FileIdExtension}]
