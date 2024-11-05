"""
Shared pytest fixtures for curb sign parser tests.
Place this file in the tests/ directory.
"""

import pytest
import json
from pathlib import Path
from PIL import Image
import io
from unittest.mock import Mock
from datetime import datetime

from curb_sign_parser import CurbSignParser
from curb_sign_parser.providers.claude import ClaudeProvider
from curb_sign_parser.providers.gpt4 import GPT4VisionProvider
from curb_sign_parser.models.data_models import SignData, CurbPolicy, Rule, TimeSpan

@pytest.fixture
def test_image_bytes():
    """Create a simple test image and return its bytes."""
    img = Image.new('RGB', (100, 100), color='white')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    return img_byte_arr.getvalue()

@pytest.fixture
def test_image_path(tmp_path, test_image_bytes):
    """Create a temporary test image file and return its path."""
    image_path = tmp_path / "test_sign.jpg"
    image_path.write_bytes(test_image_bytes)
    return str(image_path)

@pytest.fixture
def mock_claude_provider():
    """Mock Claude provider with predefined response."""
    provider = Mock(spec=ClaudeProvider)
    provider.max_image_size = 5 * 1024 * 1024
    provider.process_image.return_value = json.dumps({
        "version": "1.0",
        "currency": "USD",
        "policies": [{
            "curb_policy_id": "test-1",
            "rules": [{
                "activity": "parking",
                "max_stay": 120
            }],
            "time_spans": [{
                "days_of_week": ["mon", "tue"],
                "time_of_day_start": "09:00",
                "time_of_day_end": "17:00"
            }]
        }]
    })
    return provider

@pytest.fixture
def mock_gpt4_provider():
    """Mock GPT-4 provider with predefined response."""
    provider = Mock(spec=GPT4VisionProvider)
    provider.max_image_size = 20 * 1024 * 1024
    provider.process_image.return_value = json.dumps({
        "version": "1.0",
        "currency": "USD",
        "policies": [{
            "curb_policy_id": "test-1",
            "rules": [{
                "activity": "paid_parking",
                "rate": {
                    "rate": 2.50,
                    "rate_unit": "hour",
                    "rate_unit_period": "rolling"
                }
            }],
            "time_spans": [{
                "days_of_week": ["mon", "tue", "wed", "thu", "fri"],
                "time_of_day_start": "09:00",
                "time_of_day_end": "18:00"
            }]
        }]
    })
    return provider

@pytest.fixture
def sample_sign_data():
    """Create a sample SignData instance."""
    return SignData(
        version="1.0",
        currency="USD",
        last_updated=int(datetime.now().timestamp() * 1000),
        policies=[
            CurbPolicy(
                curb_policy_id="test-policy-1",
                rules=[
                    Rule(
                        activity="parking",
                        max_stay=120
                    )
                ],
                time_spans=[
                    TimeSpan(
                        days_of_week=["mon", "tue", "wed", "thu", "fri"],
                        time_of_day_start="09:00",
                        time_of_day_end="17:00"
                    )
                ]
            )
        ]
    )

@pytest.fixture
def test_location_data():
    """Sample location data for testing."""
    return {
        "type": "Point",
        "coordinates": [-73.9857, 40.7484]
    }

@pytest.fixture
def parser_with_claude(mock_claude_provider):
    """Create a CurbSignParser instance with mocked Claude provider."""
    parser = CurbSignParser(api_key="test-key", provider="claude")
    parser.provider = mock_claude_provider
    return parser

@pytest.fixture
def parser_with_gpt4(mock_gpt4_provider):
    """Create a CurbSignParser instance with mocked GPT-4 provider."""
    parser = CurbSignParser(api_key="test-key", provider="gpt4")
    parser.provider = mock_gpt4_provider
    return parser

@pytest.fixture
def sample_regulations():
    """Sample parking regulations for testing."""
    return [
        {
            "activity": "paid_parking",
            "max_stay": 120,
            "rate": {
                "rate": 2.50,
                "rate_unit": "hour",
                "rate_unit_period": "rolling"
            },
            "time_spans": [
                {
                    "days": ["MON", "TUE", "WED", "THU", "FRI"],
                    "start_time": "09:00",
                    "end_time": "18:00"
                }
            ]
        },
        {
            "activity": "no_parking",
            "time_spans": [
                {
                    "days": ["SAT", "SUN"],
                    "start_time": "00:00",
                    "end_time": "23:59"
                }
            ]
        }
    ]

@pytest.fixture
def sample_error_responses():
    """Sample error responses from providers."""
    return {
        "claude_error": {
            "type": "invalid_request_error",
            "message": "Invalid API key provided"
        },
        "gpt4_error": {
            "error": {
                "message": "Rate limit exceeded",
                "type": "rate_limit_error",
                "code": "rate_limit"
            }
        }
    }