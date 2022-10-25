# User guide

## Installation

The server extension can be installed from the pip registry:

```
pip install jupyter_server_fileid
```

This automatically enables the extension for your local Jupyter server
installation. You can confirm this by running

```
jupyter server extension list
```

and asserting that `jupyter_server_fileid` is enabled.

## Usage

`jupyter_server_fileid`, by default, constructs a `LocalFileIdManager` instance and
stores it under `serverapp.settings["file_id_manager"]`. This `LocalFileIdManager`
instance is a developer's way of accessing its key methods.

Once you obtain a reference to the `LocalFileIdManager` instance and bind it to some
name, e.g. `fim`, all file ID operations can be performed as methods on that
object. File ID operations are best illustrated in the following examples.

### Use case: tracking a file across moves

A common use case throughout Jupyter is to track a file even when it's moved via
shell commands that the server cannot listen to. Doing this without a File ID
manager is quite tricky, but thankfully, we have one available.

Without loss of generality, let's say the file is at the path `/server/a.txt`.
To begin, we need to **index** the file, i.e. generate a file ID for the file,
or return the existing one if one already exists.

```py
id = fim.index("/server/a.txt")
```

The file ID is guaranteed to be unique and never reused. However, there is no
restriction on its type; different configurations could return a hash string,
UUID, or integer key.

Whenever the latest path of this file is needed, resolving this is as simple as
invoking:

```py
fim.get_path(id)
```
