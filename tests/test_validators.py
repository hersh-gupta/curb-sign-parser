from curb_sign_parser.models.data_models import Location
from curb_sign_parser.utils.validators import Validators



def test_validate_time_format():
    """Test time format validation."""
    assert Validators.validate_time_format("09:00") is True
    assert Validators.validate_time_format("25:00") is False
    assert Validators.validate_time_format("9:00") is False

def test_validate_days():
    """Test day validation."""
    assert Validators.validate_days(["MON", "TUE"]) is True
    assert Validators.validate_days(["INVALID"]) is False

def test_validate_location():
    """Test location coordinate validation."""
    valid_location = Location(type="Point", coordinates=[-73.9857, 40.7484])
    assert Validators.validate_location(valid_location) is True
    
    invalid_location = Location(type="Point", coordinates=[-200, 100])
    assert Validators.validate_location(invalid_location) is False