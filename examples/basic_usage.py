from curb_sign_parser import CurbSignParser
import json
import os
import logging

logging.basicConfig(level=logging.INFO)

# Initialize parser using environment variable
api_key = os.getenv('ANTHROPIC_API_KEY')
parser = CurbSignParser(api_key=api_key)

# Parse a sign
sign_data = parser.parse_sign("IMG_5490.HEIC")

# Print the full CDS-compliant JSON
print(json.dumps(sign_data.model_dump(), indent=2))

# Print summary
print(f"\nFound {len(sign_data.policies)} policies")

for policy in sign_data.policies:
    print(f"\nPolicy ID: {policy.curb_policy_id}")
    for rule in policy.rules:
        print(f"Activity: {rule.activity}")
        if hasattr(rule, 'rate') and rule.rate:
            print(f"Rate: ${rule.rate.rate} per {rule.rate.rate_unit}")
    for time_span in policy.time_spans:
        print(f"Days: {', '.join(time_span.days_of_week)}")
        print(f"Time: {time_span.time_of_day_start} - {time_span.time_of_day_end}")