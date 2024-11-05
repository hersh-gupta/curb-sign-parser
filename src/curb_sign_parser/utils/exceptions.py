class CurbSignParserError(Exception):
    """Base exception for all curb sign parser errors."""
    pass

class ImageProcessingError(CurbSignParserError):
    """Raised when there's an error processing an image."""
    pass

class ProviderError(CurbSignParserError):
    """Raised when there's an error with an LLM provider."""
    pass

class ValidationError(CurbSignParserError):
    """Raised when there's a data validation error."""
    pass

class APIError(CurbSignParserError):
    """Raised when there's an error communicating with an API."""
    def __init__(self, message: str, status_code: int = None, response: str = None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response

class UnsupportedFormatError(CurbSignParserError):
    """Raised when an unsupported image format is encountered."""
    pass

class ConfigurationError(CurbSignParserError):
    """Raised when there's an error in the configuration."""
    pass

class ParsingError(CurbSignParserError):
    """Raised when there's an error parsing the LLM response."""
    pass