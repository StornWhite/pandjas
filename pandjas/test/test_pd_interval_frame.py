from unittest import TestCase

from pandjas.objects import FrameDef, PdIntervalFrameABC


# Create FrameDef object
frame_def = FrameDef(
    [
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


# Subclass PdIntervalFrame
class TestPdIntervalFrame(PdIntervalFrameABC):

    # PdFrame subclasses must define frame_def property
    frame_def=frame_def
    pass


class PdIntervalFrameTestCase(TestCase):

    def setUp(self):

        # Create TestPdIntervalFrame object
        self.pd_interval_frame = TestPdIntervalFrame(
            period=900,
            timezone='US/Pacific'
        )

    def test_validate_true(self):

        # Initial dataframe should be valid.
        pd_interval_frame = self.pd_interval_frame
        self.assertTrue(
            pd_interval_frame.frame_def.validate(pd_interval_frame.dataframe)
        )
