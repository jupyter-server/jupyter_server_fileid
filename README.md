# jupyter_server_fileid

[![Github Actions Status](https://github.com/jupyter-server/jupyter_server_fileid/workflows/Build/badge.svg)](https://github.com/jupyter-server/jupyter_server_fileid/actions/workflows/build.yml)

A Jupyter Server extension providing an implementation of the File ID service.

## Requirements

- Jupyter Server

## Install

To install the extension, execute:

```bash
pip install jupyter_server_fileid
```

## Uninstall

To remove the extension, execute:

```bash
pip uninstall jupyter_server_fileid
```

## Troubleshoot

If you are seeing the frontend extension, but it is not working, check
that the server extension is enabled:

```bash
jupyter server extension list
```

## Contributing

### Development install

```bash
# Clone the repo to your local environment
# Change directory to the jupyter_server_fileid directory
# Install package in development mode - will automatically enable
# The server extension.
pip install -e .
```


You can watch the source directory and run your Jupyter Server-based application at the same time in different terminals to watch for changes in the extension's source and automatically rebuild the extension.  For example,
when running JupyterLab:

```bash
jupyter lab --autoreload
```

If your extension does not depend a particular frontend, you can run the
server directly:

```bash
jupyter server --autoreload
```

### Running Tests

Install dependencies:

```bash
pip install -e ".[test]"
```

To run the python tests, use:

```bash
pytest

# To test a specific file
pytest jupyter_server_fileid/tests/test_handlers.py

# To run a specific test
pytest jupyter_server_fileid/tests/test_handlers.py -k "test_get"
```

### Development uninstall

```bash
pip uninstall jupyter_server_fileid
```

### Packaging the extension

See [RELEASE](RELEASE.md)
