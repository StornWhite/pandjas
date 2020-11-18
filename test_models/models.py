# A collection of non-abstract pandjas models for use in testing

from django.db import models

from pandjas.models import FrameModel


class TestFrameModel(FrameModel):
    """
    A non-abstract version of FrameModel for use in testing.
    """
    folder = 'pandjas_test/'
    name = models.CharField(max_length=255)
