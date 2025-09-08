"""Configuration management."""

try:
    from .settings import Settings
except ImportError:
    from .simple_settings import SimpleSettings as Settings

__all__ = ["Settings"]