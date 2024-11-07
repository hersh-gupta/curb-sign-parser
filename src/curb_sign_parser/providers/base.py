from abc import ABC, abstractmethod
from typing import Any, Dict


class LLMProvider(ABC):
    """Base class for multi-modal LLM providers."""

    def __init__(self, api_key: str, **kwargs):
        self.api_key = api_key
        self.kwargs = kwargs

    @abstractmethod
    def process_image(self, image_data: bytes) -> Dict[str, Any]:
        """
        Process an image and return structured parking rule data.

        Args:
            image_data: Raw image bytes

        Returns:
            dict: Structured parking rule data
        """
        pass

    @property
    @abstractmethod
    def max_image_size(self) -> int:
        """Maximum allowed image size in bytes."""
        pass

    @property
    def system_prompt(self) -> str:
        """System prompt for CDS-compliant parking sign analysis."""
        return """Analyze this parking sign and return the regulations as a CDS-compliant JSON object.

                Example response format:
                {
                    "version": "1.0",
                    "time_zone": "US/Eastern",
                    "last_updated": 1234567890123,
                    "currency": "USD",
                    "location": {
                        "type": "Point",
                        "coordinates": [-73.982105, 40.767932]
                    },
                    "policies": [
                        {
                            "curb_policy_id": "uuid-1234",
                            "published_date": 1234567890123,
                            "priority": 1,
                            "time_spans": [
                                {
                                    "days_of_week": ["mon", "tue", "wed", "thu", "fri"],
                                    "time_of_day_start": "09:00",
                                    "time_of_day_end": "18:00"
                                }
                            ],
                            "rules": [
                                {
                                    "activity": "paid_parking",
                                    "max_stay": 120,
                                    "rate": {
                                        "rate": 200,
                                        "rate_unit": "hour",
                                        "rate_unit_period": "rolling"
                                    }
                                }
                            ]
                        }
                    ]
                }"""
