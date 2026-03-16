"""Leanpub Multi Action is used to interact with the Leanpub.com API in GitHub Actions."""

# Gather version information from project packaging
try:
    from importlib import metadata
except ImportError:
    import importlib_metadata as metadata  # type: ignore[no-redef]

__version__ = metadata.version(__name__)
