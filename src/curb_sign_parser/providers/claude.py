import logging
from typing import Dict, Any
import base64
from anthropic import Anthropic
from .base import LLMProvider

logger = logging.getLogger(__name__)

class ClaudeProvider(LLMProvider):
    """Claude provider for multi-modal LLM processing."""
    
    def __init__(
        self,
        api_key: str,
        model: str = "claude-3-opus-20240229",
        **kwargs
    ):
        super().__init__(api_key, **kwargs)
        self.model = model
        self.client = Anthropic(api_key=api_key)

    @property
    def max_image_size(self) -> int:
        return 5 * 1024 * 1024  # 5MB
        
    def process_image(self, image_data: bytes) -> str:
        """Process image using Claude's API."""
        try:
            logger.info("Encoding image for Claude API")
            encoded_image = base64.b64encode(image_data).decode('utf-8')
            
            logger.info("Sending request to Claude API")
            message = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                system=self.system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/jpeg",
                                    "data": encoded_image
                                }
                            },
                            {
                                "type": "text",
                                "text": "Analyze this parking sign and return a CDS-compliant JSON object with the regulations."
                            }
                        ]
                    }
                ]
            )
            
            response = message.content[0].text
            logger.info(f"Received response from Claude: {response[:500]}...")  # Log first 500 chars
            return response
            
        except Exception as e:
            logger.error(f"Claude API error: {str(e)}", exc_info=True)
            raise