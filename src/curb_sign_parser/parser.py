import json
import logging
from datetime import datetime

from .models.data_models import SignData
from .processors.image_processor import ImageProcessor
from .providers.claude import ClaudeProvider
from .providers.gpt4 import GPT4VisionProvider

logger = logging.getLogger(__name__)

class CurbSignParser:
    """Parser for extracting curb rules from sign images."""

    PROVIDERS = {
        'claude': ClaudeProvider,
        'gpt4': GPT4VisionProvider
    }

    def __init__(
        self,
        api_key: str,
        provider: str = 'claude',
        **kwargs
    ):
        if provider not in self.PROVIDERS:
            raise ValueError(
                f"Unsupported provider: {provider}. "
                f"Supported providers: {', '.join(self.PROVIDERS.keys())}"
            )

        self.provider = self.PROVIDERS[provider](api_key, **kwargs)
        self.image_processor = ImageProcessor(max_size=self.provider.max_image_size)

    def _normalize_days(self, days):
        """Normalize day format to lowercase three-letter abbreviations."""
        day_mapping = {
            'MONDAY': 'mon', 'MON': 'mon', 'monday': 'mon',
            'TUESDAY': 'tue', 'TUE': 'tue', 'tuesday': 'tue',
            'WEDNESDAY': 'wed', 'WED': 'wed', 'wednesday': 'wed',
            'THURSDAY': 'thu', 'THU': 'thu', 'thursday': 'thu',
            'FRIDAY': 'fri', 'FRI': 'fri', 'friday': 'fri',
            'SATURDAY': 'sat', 'SAT': 'sat', 'saturday': 'sat',
            'SUNDAY': 'sun', 'SUN': 'sun', 'sunday': 'sun'
        }
        return [day_mapping.get(d, d.lower()) for d in days] if days else ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']

    def _normalize_time_spans(self, time_spans):
        """Normalize time spans to CDS format."""
        if not time_spans:
            return []

        normalized = []
        for span in time_spans:
            normalized_span = {
                "days_of_week": self._normalize_days(span.get("days", [])),
                "time_of_day_start": span.get("start_time", "00:00") or "00:00",
                "time_of_day_end": span.get("end_time", "23:59") or "23:59"
            }
            normalized.append(normalized_span)
        return normalized

    def _normalize_rules(self, rule):
        """Normalize rules to CDS format."""
        normalized = {
            "activity": rule.get("activity", "parking"),
        }

        if "max_stay" in rule:
            normalized["max_stay"] = rule["max_stay"]

        if "payment" in rule:
            payment = rule["payment"]
            if isinstance(payment, dict):
                normalized["rate"] = {
                    "rate": float(payment.get("rate", 0)),
                    "rate_unit": payment.get("rate_unit", "hour"),
                    "rate_unit_period": payment.get("rate_unit_period", "rolling")
                }

        if "user_classes" in rule:
            normalized["user_classes"] = rule["user_classes"]

        return normalized

    def parse_sign(self, image_path: str) -> SignData:
        """Process image and extract curb rules."""
        try:
            logger.info(f"Starting to process image: {image_path}")

            # Process image and get location data
            processed_data = self.image_processor.process_image(image_path)
            image_bytes, location_data = processed_data

            logger.info(f"Location data extracted: {location_data}")

            # Get LLM analysis
            llm_response = self.provider.process_image(image_bytes)
            logger.info(f"Raw LLM response: {llm_response[:500]}...")

            try:
                data = json.loads(llm_response)
                logger.info(f"Parsed JSON data: {json.dumps(data, indent=2)}")

                # Initialize basic structure
                cds_data = {
                    "version": "1.0",
                    "currency": "USD",
                    "last_updated": int(datetime.now().timestamp() * 1000),
                    "policies": []
                }

                # Add location if available
                if location_data:
                    cds_data["location"] = location_data

                # Convert regulations/policies
                source_policies = []
                if "regulations" in data:
                    source_policies = data["regulations"]
                elif "policies" in data:
                    source_policies = data["policies"]

                # Process each policy/regulation
                for idx, source_policy in enumerate(source_policies):
                    policy = {
                        "curb_policy_id": str(idx),
                        "published_date": int(datetime.now().timestamp() * 1000)
                    }

                    # Handle time spans
                    if "time_spans" in source_policy:
                        policy["time_spans"] = self._normalize_time_spans(source_policy["time_spans"])

                    # Handle rules
                    if "rules" in source_policy:
                        policy["rules"] = [self._normalize_rules(r) for r in source_policy["rules"]]
                    else:
                        # Convert old regulation format to rule
                        policy["rules"] = [self._normalize_rules(source_policy)]

                    # Add time spans if missing
                    if "time_spans" not in policy:
                        time_spans = source_policy.get("time_spans", [])
                        policy["time_spans"] = self._normalize_time_spans(time_spans)

                    cds_data["policies"].append(policy)

                logger.info(f"Final CDS data structure: {json.dumps(cds_data, indent=2)}")

                return SignData(**cds_data)

            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse LLM response as JSON: {e}")
                logger.debug(f"Raw response: {llm_response}")
                return SignData(
                    version="1.0",
                    currency="USD",
                    policies=[],
                    last_updated=int(datetime.now().timestamp() * 1000)
                )

        except Exception as e:
            logger.error(f"Error processing sign: {e}", exc_info=True)
            raise
