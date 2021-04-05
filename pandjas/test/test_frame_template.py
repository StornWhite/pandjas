from unittest import TestCase

from pandjas.objects import FrameDef
from pandjas.models import FrameTemplate


class FrameTemplateTestCase(TestCase):

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
        self.frame_def = FrameDef(column_def_list)

    def test_frame_template_create(self):

        template = FrameTemplate(
            name='Test Template',
            template=self.frame_def.column_defs_dict
        )
        self.assertIsInstance(template, FrameTemplate)

    def test_frame_template_save(self):

        template = FrameTemplate(
            name='Test Template',
            template=self.frame_def.column_defs_dict
        )
        template.save()
        self.assertIsInstance(template.pk, int)

    def test_frame_template_read(self):

        template = FrameTemplate(
            name='Test Template',
            template=self.frame_def.column_defs_dict
        )
        template.save()

        template = FrameTemplate.objects.get(pk=template.pk)
        self.assertIsInstance(template, FrameTemplate)
