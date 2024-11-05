"""
Curb Sign Parser
---------------
A Python package for parsing parking sign images into CDS-compliant structured data using
various multi-modal LLM providers.
"""

from .parser import CurbSignParser
from .models.data_models import (
    RegulationType,
    RateUnitPeriod,
    Rate,
    TimeSpan,
    Rule,
    CurbPolicy,
    Location,
    SignData
)
from .providers.base import LLMProvider
from .providers.claude import ClaudeProvider
from .providers.gpt4 import GPT4VisionProvider
from .utils.exceptions import (
    CurbSignParserError,
    ImageProcessingError,
    ProviderError,
    ValidationError,
    APIError,
    UnsupportedFormatError,
    ConfigurationError,
    ParsingError
)

__version__ = "0.1.0"
__author__ = "Hersh Gupta"
__email__ = "h.v.gupta@outlook.com"

# Public API
__all__ = [
    "CurbSignParser",
    # Data Models
    "RegulationType",
    "RateUnitPeriod",
    "Rate",
    "TimeSpan",
    "Rule",
    "CurbPolicy",
    "Location",
    "SignData",
    # Providers
    "LLMProvider",
    "ClaudeProvider",
    "GPT4VisionProvider",
    # Exceptions
    "CurbSignParserError",
    "ImageProcessingError",
    "ProviderError",
    "ValidationError",
    "APIError",
    "UnsupportedFormatError",
    "ConfigurationError",
    "ParsingError"
]