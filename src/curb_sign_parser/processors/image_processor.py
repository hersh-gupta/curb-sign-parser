import io
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union

import piexif
import pillow_heif
from PIL import Image

from ..utils.exceptions import ImageProcessingError

logger = logging.getLogger(__name__)

def convert_to_degrees(value) -> float:
    """
    Convert GPS coordinates stored in EXIF to degrees in float format.

    Args:
        value: Tuple of ((d_num, d_denom), (m_num, m_denom), (s_num, s_denom))

    Returns:
        float: Decimal degrees
    """
    try:
        d = float(value[0][0]) / float(value[0][1])
        m = float(value[1][0]) / float(value[1][1])
        s = float(value[2][0]) / float(value[2][1])

        return round(d + (m / 60.0) + (s / 3600.0), 6)
    except Exception as e:
        logger.error(f"Error converting GPS value {value} to degrees: {e}")
        return 0.0

def extract_location_metadata(image_path: Path) -> Optional[Dict[str, Any]]:
    """
    Extract location metadata from image EXIF data.

    Args:
        image_path: Path to the image file

    Returns:
        Optional[Dict]: Location data in CDS format or None if no location data
    """
    try:
        # Open the image
        with Image.open(image_path) as img:
            # Get EXIF data using piexif
            exif_dict = piexif.load(img.info['exif'])

            # Check if GPS data exists
            if 'GPS' not in exif_dict:
                logger.info("No GPS data found in image")
                return None

            gps_info = exif_dict['GPS']
            logger.debug(f"Found GPS info: {gps_info}")

            # Check if required GPS tags exist
            # 1: Latitude Ref (N/S), 2: Latitude, 3: Longitude Ref (E/W), 4: Longitude
            if not all(tag in gps_info for tag in [1, 2, 3, 4]):
                logger.info("Missing required GPS tags")
                return None

            # Extract latitude
            lat = convert_to_degrees(gps_info[2])
            if gps_info[1] == b'S':
                lat = -lat

            # Extract longitude
            lon = convert_to_degrees(gps_info[4])
            if gps_info[3] == b'W':
                lon = -lon

            logger.info(f"Successfully extracted coordinates: ({lat}, {lon})")

            return {
                "type": "Point",
                "coordinates": [lon, lat]  # GeoJSON format: [longitude, latitude]
            }

    except Exception as e:
        logger.error(f"Error extracting location metadata: {e}", exc_info=True)
        return None

class ImageProcessor:
    """Handles image processing and optimization for LLM providers."""

    SUPPORTED_FORMATS = {
        'jpg': 'JPEG',
        'jpeg': 'JPEG',
        'png': 'PNG',
        'heic': 'HEIF',
        'heif': 'HEIF',
        'webp': 'WEBP',
        'tiff': 'TIFF',
        'bmp': 'BMP'
    }

    def __init__(self, max_size: Optional[int] = None):
        """Initialize image processor."""
        self.max_size = max_size or (5 * 1024 * 1024)  # Default to 5MB
        self._setup_heif_support()

    def _setup_heif_support(self):
        """Configure HEIF/HEIC support."""
        try:
            pillow_heif.register_heif_opener()
            logger.info("HEIF/HEIC support initialized successfully")
        except ImportError:
            logger.error(
                "HEIC support requires pillow-heif package. "
                "Install with: pip install pillow-heif"
            )
            raise
        except Exception as e:
            logger.error(f"Failed to initialize HEIC support: {e}")
            raise

    def process_image(self, image_path: Union[str, Path]) -> Tuple[bytes, Optional[Dict[str, Any]]]:
        """
        Process image for LLM consumption and extract metadata.

        Args:
            image_path: Path to the image file

        Returns:
            Tuple[bytes, Optional[Dict]]: Processed image data and location metadata
        """
        image_path = Path(image_path)

        if not image_path.exists():
            raise FileNotFoundError(f"Image file not found: {image_path}")

        try:
            logger.info(f"Processing image: {image_path}")

            # Extract location metadata first
            location_data = extract_location_metadata(image_path)
            logger.info(f"Extracted location data: {location_data}")

            # Process image
            with Image.open(image_path) as img:
                logger.info(f"Original image format: {img.format}, mode: {img.mode}, size: {img.size}")

                # Convert to RGB if needed
                if img.mode not in ('RGB', 'RGBA'):
                    img = img.convert('RGB')
                    logger.info("Converted image to RGB mode")

                # Initial resize for very large images
                max_dimension = 2048
                width, height = img.size
                if width > max_dimension or height > max_dimension:
                    ratio = min(max_dimension / width, max_dimension / height)
                    width = int(width * ratio)
                    height = int(height * ratio)
                    img = img.resize((width, height), Image.Resampling.LANCZOS)
                    logger.info(f"Resized image to {width}x{height}")

                # Save as JPEG with optimization
                buffer = io.BytesIO()
                img.save(buffer, format='JPEG', quality=95, optimize=True)
                processed_data = buffer.getvalue()

                # Check final size
                final_size = len(processed_data)
                logger.info(f"Processed image size: {final_size/1024/1024:.2f}MB")

                if final_size > self.max_size:
                    raise ImageProcessingError(
                        f"Processed image size ({final_size/1024/1024:.2f}MB) "
                        f"exceeds maximum allowed size ({self.max_size/1024/1024:.2f}MB)"
                    )

                return processed_data, location_data

        except (pillow_heif.HeifError, OSError) as e:
            logger.error(f"Error processing image: {e}")
            raise ImageProcessingError(f"Error processing image: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error processing image: {e}")
            raise ImageProcessingError(f"Failed to process image: {str(e)}")

    def get_mime_type(self, image_path: Union[str, Path]) -> str:
        """Get MIME type for image."""
        return "image/jpeg"  # We always convert to JPEG
