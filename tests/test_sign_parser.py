import pytest
import json
from curb_sign_parser import CurbSignParser
from curb_sign_parser.models.data_models import SignData
from curb_sign_parser.providers.claude import ClaudeProvider
from curb_sign_parser.providers.gpt4 import GPT4VisionProvider
from unittest.mock import patch


def test_init_parser():
    """Test parser initialization with different providers."""
    parser = CurbSignParser(api_key="test-key", provider="claude")
    assert isinstance(parser.provider, ClaudeProvider)
    
    parser = CurbSignParser(api_key="test-key", provider="gpt4")
    assert isinstance(parser.provider, GPT4VisionProvider)
    
    with pytest.raises(ValueError):
        CurbSignParser(api_key="test-key", provider="invalid")

def test_normalize_days():
    """Test day normalization function."""
    parser = CurbSignParser(api_key="test-key")
    
    assert parser._normalize_days(["MONDAY", "FRIDAY"]) == ["mon", "fri"]
    assert parser._normalize_days(["Mon", "Fri"]) == ["mon", "fri"]
    assert parser._normalize_days([]) == ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]

@patch("curb_sign_parser.parser.ImageProcessor")
@patch("curb_sign_parser.providers.claude.ClaudeProvider")
def test_parse_sign_success(mock_provider, mock_processor):
    """Test successful sign parsing."""
    # Setup mocks
    mock_processor.return_value.process_image.return_value = (b"image_data", {"type": "Point", "coordinates": [0, 0]})
    mock_provider.return_value.process_image.return_value = json.dumps({
        "version": "1.0",
        "policies": [{
            "rules": [{"activity": "parking"}],
            "time_spans": [{"days": ["MON"], "start_time": "09:00", "end_time": "17:00"}]
        }]
    })
    
    parser = CurbSignParser(api_key="test-key")
    result = parser.parse_sign("test.jpg")
    
    assert isinstance(result, SignData)
    assert len(result.policies) == 1