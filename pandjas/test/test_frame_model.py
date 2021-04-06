from unittest import TestCase
from os.path import exists
from pandjas.objects import FrameDef
from pandjas.exceptions import InvalidDataFrameError
from test_models.models import TestFrameModel


class FrameModelTestCase(TestCase):

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

        # Create TestFrameModel
        self.tfm = TestFrameModel(
            name = 'Test Model Object',
            frame_def=frame_def,
        )
        self.tfm.save()

    def tearDown(self):
        if not self.tfm is None:
            self.tfm.delete()

    def test_frame_model_save(self):
        # Test that the django object saved successfully
        self.assertIsInstance(self.tfm.pk, int)

        # Test that the parquet file has been saved.
        self.assertTrue(exists(self.tfm.file_path))

    def test_frame_model_delete(self):
        pk = self.tfm.pk
        path = self.tfm.file_path
        self.tfm.delete()
        self.tfm = None

        # Test that the django object has been deleted.
        with self.assertRaises(TestFrameModel.DoesNotExist):
            self.tfm = TestFrameModel.objects.get(pk=pk)

        # Test that the parquet file is deleted.
        self.assertFalse(exists(path))

    def test_frame_model_validation(self):
        # Remove a required column from dataframe
        dataframe = self.tfm.dataframe.drop("energy", axis=1)
        self.tfm.dataframe = dataframe

        # Test dataframe fails validation on save.
        with self.assertRaises(InvalidDataFrameError):
            self.tfm.save()
