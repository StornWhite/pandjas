import numpy as np
import pandas as pd

import objects.exceptions as exc


class FrameDef(object):
    """
    Defines the expected format of a pandas dataframe, expressed as a
    dictionary of ColumnDef objects that describe columns that must be
    present in a dataframe for it to be valid dataframe.
    """

    @property
    def column_names(self):
        return set(self.column_defs.keys())

    @property
    def empty_dataframe(self):
        """
        Returns an empty dataframe that conforms with the frame definition.
        The dataframe will have no rows, but will have correctly named and
        typed columns

        :return: pandas dataframe
        """
        df = pd.DataFrame()
        for key, value in self.column_defs.items():
            df[key] = pd.Series(dtype=value.dtype)

        return df

    # ~~~~~~~~~~~~~~~~~~~~~~~
    # Backend methods
    # ~~~~~~~~~~~~~~~~~~~~~~~

    def __init__(self):

        self.column_defs = dict()

    # ~~~~~~~~~~~~~~~~~~~~~~~
    # User methods
    # ~~~~~~~~~~~~~~~~~~~~~~~

    def validate(self, dataframe):
        """
        Returns true if dataframe conforms to the frame definition.  To
        conform, the dataframe must have *only* those columns defined
        by the FrameDef, and those columns must match in name and dtype.

        :param dataframe:
        :return: boolean dataframe conforms
        """
        column_defs = self.column_defs.values()

        if len(column_defs) != len(dataframe.columns):
            # Missing or extra columns.
            return False

        for column_def in column_defs:

            try:
                column = dataframe[column_def.name]
            except KeyError:
                # Column is missing
                return False

            if column.dtype != column_def.dtype:
                # Column has wrong type
                return False

        return True


    def create_column_def(self, name, dtype_str, is_input=True):
        """
        Creates a ColumnDef object and adds it to the FrameDef, using the
        column name as key.

        :param name: string name of added column
        :param dtype_str: string representing a pandas dtype
        """
        column_def = ColumnDef(
            frame_def=self,
            name=name,
            dtype_str=dtype_str,
            is_input=is_input
        )
        self.column_defs[name] = column_def

    def remove_column_def(self, name):
        """
        Removes a ColumnDef object from a FrameDef. object

        :param name: string column name
        """
        try:
            self.column_defs.pop(name)
        except KeyError as e:
            pass


class ColumnDef(object):
    """
    Defines the expected format of a column in a FrameDef.

    For allowed dtype_str values see:

    https://pandas.pydata.org/pandas-docs/stable/user_guide/basics.html#dtypes
    https://numpy.org/doc/stable/reference/arrays.dtypes.html
    """

    def __init__(self, frame_def, name, dtype_str, is_input=True):
        """
        :param frame_def: related FrameDef object
        :param name: string name of column
        :param dtype_str: string corresponding to expected column dtype
        :param is_input: boolean, whether column contains input or result data
        """
        # Validate incoming data.
        if not name:
            raise exc.NoColumnDefNameError()
        self.name = name

        if frame_def is None:
            raise exc.NoColumnDefFileDefError()
        self.frame_def = frame_def

        try:
            # This syntax for getting dtypes gets both pandas and numpy dtypes
            self.dtype = pd.Series(dtype=dtype_str).dtype
        except TypeError as e:
            raise exc.IllegalDtypeStringError()

        self.is_input = is_input


class PDFrame(object):
    """
    The base-level wrapper for a pandas dataframe.  It includes both a
    dataframe and a FrameDef object which can be used to validate that
    the dataframe conforms to our data expectations.  It also includes
    base-level methods for accessing a dataframe.

    You could subclass PDFrame to create your own wrapper class with an
    explicit frame definition and your own analysis methods for performing
    high level operations and analysis on the dataframe with a goal of
    populating result column data from input column data.
    """
    @property
    def dataframe(self):
        if hasattr(self, '_dataframe'):
            return self._dataframe
        else:
            return None

    @dataframe.setter
    def dataframe(self, dataframe):
        if self.frame_def.validate(dataframe):
            self._dataframe = dataframe
        else:
            raise exc.InvalidDataFrameError

    def __init__(self, frame_def=None, dataframe=None):
        """
        Sets or creates the PDFrame objects frame definition and initial
        dataframe.

        :param frame_def: FrameDef object
        :param dataframe: panadas dataframe object
        """
        if frame_def is None:
            self.frame_def = FrameDef()
        else:
            self.frame_def = frame_def

        if dataframe is None:
            # Todo: actually create a conforming but empty dataframe
            self.dataframe = self.frame_def.empty_dataframe
        else:
            self.dataframe = dataframe


