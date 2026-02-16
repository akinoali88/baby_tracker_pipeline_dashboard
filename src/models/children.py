''' 
Create child classes to represent children and their feeding data.
The inputs here are based on the options available in the Baby Tracker app.
For the purpose of simplicity, this app only considers feeding data.
'''

from datetime import date, datetime
from enum import Enum
from typing import List

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

minimum_date = date(2000, 1, 1)

class Sex(str, Enum):

    '''Sex options for children'''

    MALE = 'Male'
    FEMALE = 'Female'
    PREFER_NOT_TO_SAY = 'Prefer not to say'

class Activity(str, Enum):

    '''Types of activities logged for a child'''

    FEEDING = 'Feeding'

class ActivityType(str, Enum):

    '''Types of activities
    For simplicity, only feeding types are included here.
    '''

    # ===============================
    # Feed types
    # ===============================

    LEFT = 'Left'           # refers to breastfeeding side
    RIGTH = 'Right'         # refers to breastfeeding side
    BOTTLE = 'Bottle'

class Units(str, Enum):

    '''Units for feeding amount'''

    OUNCES = 'oz'
    MILLILITERS = 'ml'

class MilkType(str, Enum):

    '''Types of milk per individual feed'''

    FORMULA = 'Formula'
    BREAST_MILK = 'Breast Milk'

class FeedingData(BaseModel):

    '''Class representing feeding data for a child'''

    feed_start_time: datetime
    activity: Activity
    type: ActivityType
    feed_volume_ml: float = Field(ge=0, description='volumne of milk consumed')
    units: str = Field(default='ml')

class ChildConfig(BaseModel):

    '''Schema for an individual child's data'''
    name: str
    file_name: str
    dob: date

class AppSettings(BaseSettings):

    '''Main settings class that reads from .env'''
    # Define your children as a list of configs
    # Pydantic can parse JSON strings from .env into lists of objects!
    children: List[ChildConfig]

    # Tell Pydantic to look for a .env file
    model_config = SettingsConfigDict(env_file='.env',
                                      env_file_encoding='utf-8',
                                      extra='ignore')

# Create a singleton instance to use throughout your app
settings = AppSettings()
