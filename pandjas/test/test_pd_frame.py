from unittest import TestCase

import pandas as pd

from pandjas.objects import FrameDef, PdFrameABC


# Create FrameDef object
frame_def = FrameDef(
    [
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
)


# Subclass PdFrame
class TestPdFrame(PdFrameABC):

    # PdFrame subclasses must define frame_def property
    frame_def=frame_def
    pass


class PdFrameTestCase(TestCase):

    def setUp(self):

        # Create empty dataframe
        dataframe = frame_def.empty_dataframe

        # Create PdFrame object
        self.pd_frame = TestPdFrame(dataframe)

    def test_validate_valid(self):

        # Initial dataframe should be valid.
        pd_frame = self.pd_frame
        self.assertTrue(
            pd_frame.frame_def.validate(pd_frame.dataframe)
        )

    def test_remove_column_def(self):
        """
        Removing a column_def from the frame_def should result in a
        valid dataframe becoming invalid.
        """
        # Initial dataframe should be valid.
        pd_frame = self.pd_frame
        self.assertTrue(
            pd_frame.frame_def.validate(pd_frame.dataframe)
        )
        # Now remove a ColumnDef from the FrameDef
        del pd_frame.frame_def.column_defs[0]
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
