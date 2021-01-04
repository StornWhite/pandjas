from unittest import TestCase

import pandas as pd

from pandjas.objects import FrameDef
from pandjas.models import FrameTemplate
from pandjas.exceptions import InvalidDataFrameError
from test_models.models import TestIntervalModel


class IntervalModelTestCase(TestCase):

    def setUp(self):

        # Create FrameDef object
        frame_def = FrameDef()
        frame_def.create_column_def(
            "timestamp",
            "datetime64[ns, US/Pacific]"
        )
        frame_def.create_column_def(
            "power",
            "float"
        )
        frame_def.create_column_def(
            "customer_id",
            "UInt64"
        )
        frame_def.create_column_def(
            "energy",
            "float",
            is_input=False
        )

        # Create FrameTemplate
        template = FrameTemplate(
            name='Test Template',
            template=frame_def.column_defs_dict
        )
        template.save()

        # Create TestIntervalModel
        self.tim = TestIntervalModel(
            name = 'Test Model Object',
            frame_template=template,
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
