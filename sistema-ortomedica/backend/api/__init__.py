"""Package marker for backend.api

This file makes the `api` folder an importable Python package which
helps `python -m uvicorn api.main:app` reliably import the module
when running from the `backend` folder.
"""

__all__ = ["main", "webhook_app"]
