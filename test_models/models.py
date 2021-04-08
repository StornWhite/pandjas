# A collection of non-abstract pandjas models for use in testing

from django.db import models

from pandjas.objects import FrameDef
from pandjas.models import FrameModelABC, IntervalModelABC


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


class TestFrameModel(FrameModelABC):
    """
    A non-abstract version of FrameModel for use in testing.
    """
    frame_def = frame_def
    folder = 'pandjas_test/'
    name = models.CharField(max_length=255)


class TestIntervalModel(IntervalModelABC):
    """
    A non-abstract version of IntervalModel for use in testing.
    """
    frame_def = frame_def
    folder = 'pandjas_test/'
    name = models.CharField(max_length=255)
