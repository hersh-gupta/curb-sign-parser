import pytest
from curb_sign_parser.models.data_models import SignData, TimeSpan
from curb_sign_parser.utils.exceptions import ValidationError

def test_sign_data_model():
    """Test SignData model creation and validation."""
    data = {
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
    }
    
    sign_data = SignData(**data)
    assert sign_data.version == "1.0"
    assert len(sign_data.policies) == 1
    assert sign_data.policies[0].rules[0].max_stay == 120

def test_time_span_model():
    """Test TimeSpan model validation."""
    valid_data = {
        "days_of_week": ["mon", "tue"],
        "time_of_day_start": "09:00",
        "time_of_day_end": "17:00"
    }
    time_span = TimeSpan(**valid_data)
    assert len(time_span.days_of_week) == 2
    
    invalid_data = {
        "days_of_week": ["invalid_day"],
        "time_of_day_start": "09:00",
        "time_of_day_end": "17:00"
    }
    with pytest.raises(ValidationError):
        TimeSpan(**invalid_data)
