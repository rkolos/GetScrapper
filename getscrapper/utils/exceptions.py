"""Custom exceptions for GetScrapper."""


class GetScrapperError(Exception):
    """Base exception for GetScrapper."""

    def __init__(self, message: str, error_code: str = None) -> None:
        super().__init__(message)
        self.message = message
        self.error_code = error_code


class ParsingError(GetScrapperError):
    """Raised when parsing fails."""

    def __init__(self, message: str, parser_type: str = None) -> None:
        super().__init__(message, "PARSING_ERROR")
        self.parser_type = parser_type


class StorageError(GetScrapperError):
    """Raised when storage operations fail."""

    def __init__(self, message: str, storage_type: str = None) -> None:
        super().__init__(message, "STORAGE_ERROR")
        self.storage_type = storage_type


class ConfigurationError(GetScrapperError):
    """Raised when configuration is invalid."""

    def __init__(self, message: str) -> None:
        super().__init__(message, "CONFIG_ERROR")


class NetworkError(GetScrapperError):
    """Raised when network operations fail."""

    def __init__(self, message: str, status_code: int = None) -> None:
        super().__init__(message, "NETWORK_ERROR")
        self.status_code = status_code