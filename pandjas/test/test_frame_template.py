from unittest import TestCase

from pandjas.objects import FrameDef
from pandjas.models import FrameTemplate


class FrameTemplateTestCase(TestCase):

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
        self.frame_def = frame_def

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
