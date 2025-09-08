"""Storage modules for different output formats."""

try:
    from .csv_storage import CSVStorage
except ImportError:
    from .simple_csv_storage import SimpleCSVStorage as CSVStorage

from .json_storage import JSONStorage
from .base_storage import BaseStorage

__all__ = ["CSVStorage", "JSONStorage", "BaseStorage"]