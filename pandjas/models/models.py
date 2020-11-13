from os import path
from uuid import uuid4

from django.db import models
from django.conf import settings

from pandjas.objects.objects import PdFrame


class ValidatingModel(models.Model):
    """
    An abstract django model that self-validates by calling full_clean()
    during save.  This in turn validates all model fields.  Subclasses of
    this model can implement object-wide validation (across multiple fields,
    etc) by implementing the clean() method.
    """
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        abstract = True


class FrameModel(ValidatingModel, PdFrame):
    """
    Subclasses of this abstract django model are automatically linked to a
    pandas dataframe that is automatically assigned a unique name and stored
    in a subdirectory of the django media_root folder
    """
    # Path to folder within media_root where dataframe files will be stored
    # Override this to customize.
    folder = 'pandjas/'

    frame_file = models.FileField(
        upload_to=folder,
        blank=True
    )

    class Meta:
        abstract = True

    @property
    def file_name(self):
        """
        Gets or creates a filename for the stored parfait-formatted pandas
        dataframe related to a FrameModel object.  If file_name isn't already
        stored as a model property, we get it from the FileField
        :return:
        """
        if not hasattr(self, '_file_name'):
            try:
                # Get file name from file field.
                name = self.frame_file.name
                if name is None or not len(name):
                    raise ValueError()
            except ValueError:
                # Create file name as uuid.
                self._file_name = '{}.parquet'.format(uuid4())

        return self._file_name

    @property
    def file_path(self):
        """
        Caches and returns the path to the associated parfait file.
        """
        if not hasattr(self, '_file_path'):
            file_path = settings.MEDIA_ROOT
            file_path = path.join(file_path, self.folder)
            file_path = path.join(file_path, self.file_name)
            self._file_path = file_path

        return self._file_path

    def __init__(self, *args, **kwargs):
        """
        Attaches a FrameDef and/or a Dataframe object  if either is passed as
        an argument.
        """
        frame_def = kwargs.pop('frame_def', None)
        dataframe = kwargs.pop('dataframe', None)

        # Initialize the django model
        ValidatingModel.__init__(self, *args, **kwargs)

        # Add in the frame_def and dataframe
        PdFrame.__init__(
            self,
            frame_def=frame_def,
            dataframe=dataframe
        )
