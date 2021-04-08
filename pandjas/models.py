from os import path
from uuid import uuid4
from threading import Thread
from abc import ABCMeta

import pandas as pd

from django.db import models
from django.conf import settings
from timezone_field import TimeZoneField

from utils.time import get_period_as_timedelta
from pandjas.objects import FrameDef, PdFrameABC, PdIntervalFrameABC
from pandjas.exceptions import InvalidDataFrameError


class ValidatingModelABC(models.Model):
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


class ModelAMCMeta(models.base.ModelBase, ABCMeta):
    """
    This metaclass subclasses the metaclass for Django's Model class and
    python's built-in ABCMeta, which is the metaclass for Abstract Base
    Classes.  We need to create this metaclass explictly in order to
    subclass both Model and ABC.
    """
    pass


class FrameModelABC(ValidatingModelABC, PdFrameABC, metaclass=ModelAMCMeta):
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
                self._dataframe = self.get_empty_dataframe()
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

        :param frame_def: FrameDef object defining dataframe formating
        :param dataframe: optional dataframe object, must conform to FrameDef
        """
        dataframe = kwargs.pop('dataframe', None)

        # Initialize the django model
        ValidatingModelABC.__init__(self, *args, **kwargs)

        # Add in the frame_def and dataframe
        PdFrameABC.__init__(
            self,
            dataframe=dataframe
        )

    # Todo: Storn think whether it makes sense to get empty dataframe vs error
    def _get_or_create_dataframe(self):
        """
        Reads dataframe from file, if possible.  Otherwise opens an empty
        dataframe.
        :return:
        """
        try:
            self._dataframe = pd.read_parquet(self.frame_file)
        except (FileNotFoundError, ValueError):
            self._dataframe = self.get_empty_dataframe()

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


class IntervalModelABC(
    PdIntervalFrameABC, FrameModelABC, metaclass=ModelAMCMeta
):
    """
    A FrameModel subclass for storing periodic data.  Subclassing
    PDIntervalFrame provides access to init and validation methods for
    periodic data.
    """
    timezone = TimeZoneField(default='US/Pacific')
    # Period is stored as iso duration string but returned as a Timedelta
    period_str = models.CharField(
        max_length=12
    )

    class Meta:
        abstract = True

    # ~~~~~~~~~~~~~~~~~~~~~~~
    # Properties:
    # ~~~~~~~~~~~~~~~~~~~~~~~
    @property
    def period(self):
        if not hasattr(self, '._period'):
            self._period = pd.Timedelta(self.period_str)

        return self._period

    @period.setter
    def period(self, period):
        # Accepts input as integer, pd frequency str, or Timedelta object.
        self._period = get_period_as_timedelta(period)
        self.period_str = self._period.isoformat()

    # ~~~~~~~~~~~~~~~~~~~~~~~
    # Backend methods:
    # ~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, *args, **kwargs):
        """
        Attaches a FrameDef and/or a Dataframe object  if either is passed as
        an argument, as well as initializing timezone and period.
        """
        dataframe = kwargs.pop('dataframe', None)
        period = kwargs.pop('period', None)
        timezone = kwargs.get('timezone', None)

        self.period = get_period_as_timedelta(period)
        if type(period) is str:
            kwargs['period_str'] = period
        else:
            kwargs['period_str'] = self.period.isoformat()

        # Initialize the django model
        ValidatingModelABC.__init__(self, *args, **kwargs)

        # Add in the frame_def and dataframe
        PdIntervalFrameABC.__init__(
            self,
            period=period,
            timezone=timezone,
            dataframe=dataframe
        )
