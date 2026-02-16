'''
Unit tests for the Baby Tracker Pydantic models.

This module validates the data integrity, constraint enforcement, and 
default value logic for the FeedingData model and its associated Enums.

'''

import unittest
from datetime import datetime
from pydantic import ValidationError
from src.models.children import FeedingData, Activity, ActivityType

class TestFeedingData(unittest.TestCase):
    '''
    Tests cover:
    - Successful instantiation with valid data.
    - Constraint validation (e.g., non-negative volume).
    - Automatic type coercion for strings to datetime objects.
    - Enum membership verification for activities and types.
    '''

    def setUp(self):
        '''Set up valid base data for reuse.'''
        self.valid_data = {
            'feed_start_time': datetime(2023, 10, 27, 10, 30),
            'activity': Activity.FEEDING,
            'type': ActivityType.BOTTLE,
            'feed_volume_ml': 120.5,
            'units': 'ml'
        }

    def test_feeding_data_success(self):
        '''Test that a valid dictionary creates a FeedingData instance successfully.'''
        feeding = FeedingData(**self.valid_data)

        self.assertEqual(feeding.feed_volume_ml, 120.5)
        self.assertEqual(feeding.activity, Activity.FEEDING)
        self.assertIsInstance(feeding.feed_start_time, datetime)

    def test_default_units(self):
        '''Test that 'units' defaults to 'ml' if not provided.'''
        data_no_units = self.valid_data.copy()
        del data_no_units['units']

        feeding = FeedingData(**data_no_units)
        self.assertEqual(feeding.units, 'ml')

    def test_invalid_volume_negative(self):
        '''Test that a negative feed_volume_ml raises a ValidationError.'''
        invalid_data = self.valid_data.copy()
        invalid_data['feed_volume_ml'] = -5.0

        with self.assertRaises(ValidationError) as context:
            FeedingData(**invalid_data)

        # Check if the error is specifically about the 'ge' (greater than or equal to) constraint
        self.assertIn('greater than or equal to 0', str(context.exception))

    def test_invalid_activity_enum(self):
        '''Test that an invalid enum value for activity raises a ValidationError.'''
        invalid_data = self.valid_data.copy()
        invalid_data['activity'] = 'Sleeping'  # Only feeding is valid

        with self.assertRaises(ValidationError):
            FeedingData(**invalid_data)

    def test_type_coercion(self):
        '''Test Pydantic's ability to coerce strings to datetimes.'''
        data_str_date = self.valid_data.copy()
        data_str_date['feed_start_time'] = '2023-10-27T10:30:00'

        feeding = FeedingData(**data_str_date)
        self.assertEqual(feeding.feed_start_time, datetime(2023, 10, 27, 10, 30))

if __name__ == '__main__':
    unittest.main()
