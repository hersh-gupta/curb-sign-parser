import json
from unittest.mock import patch
from curb_sign_parser.providers.claude import ClaudeProvider
from curb_sign_parser.providers.gpt4 import GPT4VisionProvider


def test_claude_provider():
    """Test Claude provider initialization and properties."""
    provider = ClaudeProvider(api_key="test-key")
    assert provider.max_image_size == 5 * 1024 * 1024
    assert provider.api_key == "test-key"

def test_gpt4_provider():
    """Test GPT-4 provider initialization and properties."""
    provider = GPT4VisionProvider(api_key="test-key")
    assert provider.max_image_size == 20 * 1024 * 1024
    assert provider.api_key == "test-key"

@patch("requests.post")
def test_gpt4_process_image(mock_post):
    """Test GPT-4 Vision image processing."""
    mock_post.return_value.json.return_value = {
        "choices": [{
            "message": {
                "content": json.dumps({"version": "1.0", "policies": []})
            }
        }]
    }
    
    provider = GPT4VisionProvider(api_key="test-key")
    result = provider.process_image(b"test_image")
    
    assert isinstance(result, str)
    mock_post.assert_called_once()