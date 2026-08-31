"""cPanel/Phusion Passenger WSGI entry point for LTMD Analytics.

The cPanel application root should be the repository checkout (or a deployment copy of it).
Private data paths are supplied through environment variables and must stay outside public_html
and outside the Git repository.
"""
from analytics_api.app import application  # noqa: F401
