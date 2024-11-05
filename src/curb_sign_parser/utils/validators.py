from typing import Dict, List, Optional, Union
import re
from datetime import datetime
from ..models.data_models import TimeSpan, Location, Rate, RateUnitPeriod

class Validators:
    """Validation utilities for curb sign data."""
    
    @staticmethod
    def validate_time_format(time_str: str) -> bool:
        """
        Validate time string format (HH:MM).
        
        Args:
            time_str: Time string to validate
            
        Returns:
            bool: True if valid
        """
        try:
            datetime.strptime(time_str, "%H:%M")
            return True
        except ValueError:
            return False

    @staticmethod
    def validate_days(days: List[str]) -> bool:
        """
        Validate list of days.
        
        Args:
            days: List of day abbreviations
            
        Returns:
            bool: True if valid
        """
        valid_days = {
            "MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN",
            "MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY",
            "FRIDAY", "SATURDAY", "SUNDAY"
        }
        return all(day.upper() in valid_days for day in days)

    @staticmethod
    def validate_time_span(time_span: TimeSpan) -> bool:
        """
        Validate a TimeSpan object.
        
        Args:
            time_span: TimeSpan to validate
            
        Returns:
            bool: True if valid
        """
        if not Validators.validate_days(time_span.days):
            return False
            
        if not (Validators.validate_time_format(time_span.start_time) and 
                Validators.validate_time_format(time_span.end_time)):
            return False
            
        # Validate time order
        start = datetime.strptime(time_span.start_time, "%H:%M")
        end = datetime.strptime(time_span.end_time, "%H:%M")
        return start <= end

    @staticmethod
    def validate_duration(minutes: int) -> bool:
        """
        Validate time duration in minutes.
        
        Args:
            minutes: Duration in minutes
            
        Returns:
            bool: True if valid
        """
        return minutes > 0

    @staticmethod
    def validate_location(location: Location) -> bool:
        """
        Validate geographic coordinates.
        
        Args:
            location: Location object with coordinates
            
        Returns:
            bool: True if valid
        """
        try:
            lon, lat = location.coordinates
            return -180 <= lon <= 180 and -90 <= lat <= 90
        except (TypeError, IndexError):
            return False

    @staticmethod
    def validate_rate(rate: Rate) -> bool:
        """
        Validate rate information.
        
        Args:
            rate: Rate object
            
        Returns:
            bool: True if valid
        """
        valid_units = {"minute", "hour", "day", "month", "year"}
        return (
            rate.rate >= 0 and
            rate.rate_unit.lower() in valid_units and
            isinstance(rate.rate_unit_period, RateUnitPeriod)
        )