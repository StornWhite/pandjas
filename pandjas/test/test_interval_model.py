from unittest import TestCase

import pandas as pd

from pandjas.objects import FrameDef
from test_models.models import TestIntervalModel


class IntervalModelTestCase(TestCase):

    def setUp(self):

        # Create FrameDef object
        column_def_list = [
            {
                "name": "timestamp",
                "dtype_str": "datetime64[ns, US/Pacific]"
            },
            {
                "name": "power",
                "dtype_str": "float"
            },
            {
                "name": "customer_id",
                "dtype_str": "UInt64"
            },
            {
                "name": "energy",
                "dtype_str": "float",
                "is_input": False
            }
        ]
        frame_def = FrameDef(column_def_list)

        # Create TestIntervalModel
        self.tim = TestIntervalModel(
            name='Test Model Object',
            timezone='US/Pacific',
            period='900s'
        )
        self.tim.save()

    def tearDown(self):
        if not self.tim is None:
            self.tim.delete()

    def test_inverval_model_timezone_validation(self):

        # Replace dataframe index with different timezone
        dataframe = self.tim.dataframe
        idx = pd.DatetimeIndex(
            [],
            tz='UTC',
            freq=self.tim.dataframe.index.freq,
            name='timestamp'
        )
        dataframe.set_index(idx, inplace=True)

        # Test dataframe fails validation.
        self.assertFalse(self.tim.validate(dataframe))

    def test_interval_model_period_validation(self):

        # Change dataframe index frequency.
        dataframe = self.tim.dataframe
        dataframe.index.freq = '100s'

        # Test dataframe fails validation.
        self.assertFalse(self.tim.validate(dataframe))
