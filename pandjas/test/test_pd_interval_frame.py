from unittest import TestCase

from pandjas.objects import FrameDef, PdIntervalFrame


class PdIntervalFrameTestCase(TestCase):

    def setUp(self):

        # Create FrameDef object
        column_def_list = [
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

        # Create PdIntervalFrame object
        self.pd_interval_frame = PdIntervalFrame(
            period=900,
            timezone='US/Pacific',
            frame_def=frame_def
        )

    def test_validate_true(self):

        # Initial dataframe should be valid.
        pd_interval_frame = self.pd_interval_frame
        self.assertTrue(
            pd_interval_frame.frame_def.validate(pd_interval_frame.dataframe)
        )
