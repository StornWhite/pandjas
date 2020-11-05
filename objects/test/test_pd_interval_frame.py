from unittest import TestCase

from objects.objects import FrameDef, PdIntervalFrame


class PdIntervalFrameTestCase(TestCase):

    def setUp(self):

        # Create FrameDef object
        frame_def = FrameDef()
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
