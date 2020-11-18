from os import path
from uuid import uuid4
from threading import Thread

import pandas as pd

from django.db import models
from django.conf import settings

from pandjas.objects import FrameDef, PdFrame
from pandjas.exceptions import InvalidDataFrameError


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


class FrameTemplate(ValidatingModel, FrameDef):
    """
    Like a FrameDef, FrameTemplate is used to validate Dataframe formatting.
    However, FrameTemplate objects persist as django models, with all the
    formatting data stored in a json field.
    """
    name = models.CharField(
        max_length=255
    )
    template = models.JSONField()

    def __init__(self, *args, **kwargs):
        """
        Imports column definitions from JSON.
        """
        # Look in kwargs for column definitions:
        column_defs_dict = kwargs.pop('column_defs_dict', None)

        # Initializes djando model
        ValidatingModel.__init__(self, *args, **kwargs)

        if column_defs_dict:
            # Initialize with column definitions
            FrameDef.__init__(self, self.column_defs_dict)
        else:
            # Load column definitions from db
            FrameDef.__init__(self, self.template)

    def save(self, *args, **kwargs):
        """
        Saves FrameDef's dictionary of column definition's as JSON in the
        template field.
        """
        self.template = self.column_defs_dict
        super().save(*args, **kwargs)


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
    frame_template = models.ForeignKey(
        FrameTemplate,
        on_delete=models.PROTECT
    )

    class Meta:
        abstract = True

    # ~~~~~~~~~~~~~~~~~~~~~~~
    # Properties:
    # ~~~~~~~~~~~~~~~~~~~~~~~
    @property
    def dataframe(self):
        if not hasattr(self, '_dataframe'):
            thread = Thread(
                target=self._get_or_create_dataframe
            )
            thread.start()
            thread.join(timeout=30)
            self.frame_file.close()
            if thread.is_alive():
                self._dataframe = self.frame_template.get_empty_dataframe()
        return self._dataframe

    @dataframe.setter
    def dataframe(self, dataframe):
        self._dataframe = dataframe

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
            file_path = path.join(file_path, self.file_name)
            self._file_path = file_path

        return self._file_path

    # ~~~~~~~~~~~~~~~~~~~~~~~
    # Backend methods:
    # ~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, *args, **kwargs):
        """
        Attaches a FrameDef and/or a Dataframe object  if either is passed as
        an argument.
        """
        dataframe = kwargs.pop('dataframe', None)

        # Initialize the django model
        ValidatingModel.__init__(self, *args, **kwargs)

        # Add in the frame_def and dataframe
        PdFrame.__init__(
            self,
            frame_def=FrameDef(
                column_defs_dict=self.frame_template.template
            ),
            dataframe=dataframe
        )

    # Todo: Storn check whether it makes sense to get empty dataframe vs error
    def _get_or_create_dataframe(self):
        """
        Reads dataframe from file, if possible.  Otherwise opens an empty
        dataframe.
        :return:
        """
        try:
            self._dataframe = pd.read_parquet(self.frame_file)
        except (FileNotFoundError, ValueError):
            self._dataframe = self.frame_template.empty_dataframe

    # ~~~~~~~~~~~~~~~~~~~~~~~
    # User methods:
    # ~~~~~~~~~~~~~~~~~~~~~~~

    def save(self, *args, **kwargs):
        """
        Saves dataframe to media folder.
        """
        # Validate dataframe
        if self.validate(self.dataframe) is False:
            raise InvalidDataFrameError()

        # Save dataframe to disk
        self.dataframe.to_parquet(self.file_path)

        # Update django FileField
        relative_path = path.join(self.folder, self.file_name)
        self.frame_file = relative_path

        super().save()

    def delete(self, *args, **kwargs):
        """
        Deletes dataframe from media folder prior to deleting model.
        """
        storage = self.frame_file.storage
        storage.delete(self.file_path)

        super().delete(*args, **kwargs)
