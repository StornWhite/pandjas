from unittest import TestCase

import pandas as pd

from pandjas.objects.objects import FrameDef, PdFrame


class PdFrameTestCase(TestCase):

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

        # Create empty dataframe
        dataframe = frame_def.empty_dataframe

        # Create PdFrame object
        self.pd_frame = PdFrame(frame_def, dataframe)

    def test_validate_valid(self):

        # Initial dataframe should be valid.
        pd_frame = self.pd_frame
        self.assertTrue(
            pd_frame.frame_def.validate(pd_frame.dataframe)
        )

    def test_remove_column_def(self):
        """
        Removing a column_def from the frame_def should result in a
        valid dataframe becomeing invalid.
        """
        # Initial dataframe should be valid.
        pd_frame = self.pd_frame
        self.assertTrue(
            pd_frame.frame_def.validate(pd_frame.dataframe)
        )
        # Now remove a ColumnDef from the FrameDef
        pd_frame.frame_def.remove_column_def('power')
        self.assertFalse(
            pd_frame.frame_def.validate(pd_frame.dataframe)
        )

    def test_validate_invalid_columns(self):

        # Drop a required column
        pd_frame = self.pd_frame
        pd_frame.dataframe.drop('power', axis=1, inplace=True)
        self.assertFalse(
            pd_frame.frame_def.validate(pd_frame.dataframe)
        )

    def test_validate_invalid_dtype(self):

        # Change a required dtype
        pd_frame = self.pd_frame
        pd_frame.dataframe.drop('power', axis=1)
        pd_frame.dataframe['power'] = pd.Series(dtype='UInt64').dtype
        self.assertFalse(
            pd_frame.frame_def.validate(pd_frame.dataframe)
        )
