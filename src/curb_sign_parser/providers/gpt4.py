import requests
import logging
from typing import Dict, Any
import base64
from .base import LLMProvider

logger = logging.getLogger(__name__)

class GPT4VisionProvider(LLMProvider):
    """GPT-4 Vision provider for multi-modal LLM processing."""
    
    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4-vision-preview",
        **kwargs
    ):
        super().__init__(api_key, **kwargs)
        self.model = model
        self.api_url = "https://api.openai.com/v1/chat/completions"

    @property
    def max_image_size(self) -> int:
        return 20 * 1024 * 1024  # 20MB
        
    def process_image(self, image_data: bytes) -> Dict[str, Any]:
        """Process image using GPT-4 Vision API."""
        try:
            encoded_image = base64.b64encode(image_data).decode('utf-8')
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": self.system_prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{encoded_image}"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": 1024
            }

            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
            
        except Exception as e:
            logger.error(f"GPT-4 Vision API error: {str(e)}")
            raise