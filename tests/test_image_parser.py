import pytest
from PIL import Image
import io

from curb_sign_parser.processors.image_processor import ImageProcessor
from curb_sign_parser.utils.exceptions import ImageProcessingError

def create_test_image():
    """Helper to create a test image."""
    img = Image.new('RGB', (100, 100), color='white')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    return img_byte_arr.getvalue()

def test_image_processor_init():
    """Test ImageProcessor initialization."""
    processor = ImageProcessor()
    assert processor.max_size == 5 * 1024 * 1024
    
    processor = ImageProcessor(max_size=1000000)
    assert processor.max_size == 1000000

def test_process_image_size_limit():
    """Test image size limit enforcement."""
    processor = ImageProcessor(max_size=100)  # Very small limit
    
    with pytest.raises(ImageProcessingError):
        processor.process_image(create_test_image())