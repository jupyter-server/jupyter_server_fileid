"""A Jupyter Server extension providing an implementation of the File ID service."""

from typing import Any, Dict, List

from .extension import FileIdExtension

__version__ = "0.9.3"


def _jupyter_server_extension_points() -> List[Dict[str, Any]]:
    return [{"module": "jupyter_server_fileid", "app": FileIdExtension}]
