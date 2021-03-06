from abc import ABC, abstractmethod

import pandas as pd
import pytz

from utils.time import get_period_as_timedelta
import pandjas.exceptions as exc


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
        for column_def in self.column_defs:
            df[column_def.name] = pd.Series(dtype=column_def.dtype)

        return df

    @property
    def column_def_list(self):
        """
        This list defines the formatting of a dataframe.  It can be used to
        init a FrameDef object.

        format is:
        [
            {
            "name": <column_name>,
            "dtype_str": <pandas_dtype_string>,
            "is_input": <boolean>
            },
            ...
        ]
        :return: list
        """

        column_def_list = []

        for column_def in self.column_defs:
            column_def_list.append(column_def.column_def_dict)

        return column_def_list

    @property
    def column_names(self):
        """
        Returns the column names as a set.
        :return: set of column names
        """
        names = set()
        for column_def in self.column_defs:
            names.add(column_def.name)

        return names

    # ~~~~~~~~~~~~~~~~~~~~~~~
    # Backend methods
    # ~~~~~~~~~~~~~~~~~~~~~~~

    def __init__(self, column_def_list=None):
        """
        Initializes column_defs, which is the list of ColumnDef objects that
        define dataframe formatting, from a column_def_list with format:

        [
            {
            "name": <column_name>,
            "dtype_str": <pandas_dtype_string>,
            "is_input": <boolean>
            },
            ...
        ]

        or creates empty column_defs if no input.

        :param column_def_list: list of column attributes.
        """
        self.column_defs = []

        if column_def_list is not None:
            for definition_dict in column_def_list:
                column_def = ColumnDef(
                    frame_def=self,
                    name=definition_dict.get('name'),
                    dtype_str=definition_dict.get('dtype_str'),
                    is_input=definition_dict.get('is_input', True)
                )
                self.column_defs.append(column_def)

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
        column_defs = self.column_defs

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


class ColumnDef(object):
    """
    Defines the expected format of a column in a FrameDef.

    For allowed dtype_str values see:

    https://pandas.pydata.org/pandas-docs/stable/user_guide/basics.html#dtypes
    https://numpy.org/doc/stable/reference/arrays.dtypes.html
    """

    @property
    def column_def_dict(self):
        """
        A dictionary that defines a ColumnDef format.

        :return: dict
        """

        column_def_dict = dict()

        column_def_dict['name'] = self.name
        column_def_dict['dtype_str'] = str(self.dtype)
        column_def_dict['is_input'] = self.is_input

        return column_def_dict

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

        if name in frame_def.column_names:
            raise exc.DuplicateColumnDefNameError()

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


class PdFrameABC(ABC):
    """
    The base-level wrapper for a pandas dataframe.  It includes both a
    dataframe and a FrameDef object which can be used to validate that
    the dataframe conforms to our data expectations.  It also includes
    base-level methods for accessing a dataframe.

    This is an abstract base class.  You could subclass PdFrame to create
    your own wrapper class with an explicit frame definition and your own
    analysis methods for performing high level operations and analysis on
    the dataframe with a goal of populating result column data from input
    column data.
    """
    @property
    @abstractmethod
    def frame_def(self):
        """
        Override this with an instance of the FrameDef class, which will
        define the expected formatting of the dataframe.
        """
        raise NotImplementedError("Child class must override frame_def.")

    @property
    def dataframe(self):
        if hasattr(self, '_dataframe'):
            return self._dataframe
        else:
            return None

    @dataframe.setter
    def dataframe(self, dataframe):

        if self.validate(dataframe):
            self._dataframe = dataframe
        else:
            raise exc.InvalidDataFrameError

    def __init__(self, dataframe=None):
        """
        Sets or creates the PdFrame objects frame definition and initial
        dataframe.

        :param dataframe: panadas dataframe object
        """

        if dataframe is None:
            # Create conforming but empty dataframe
            self.dataframe = self.get_empty_dataframe()
        else:
            # Validate incoming dataframe
            if self.validate(dataframe):
                self._dataframe = dataframe
            else:
                raise exc.InvalidDataFrameError

    def validate(self, dataframe):
        """
        Validates dataframe by passing it through to FrameDef.  This method
        could be overridden in subclasses to provide more sophisticated
        data validation, beyond column type checking.

        :param dataframe: pandas dataframe object
        :return: boolean dataframe conforms
        """
        return self.frame_def.validate(dataframe)

    def get_empty_dataframe(self):
        """
        Returns a dataframe with correctly formatted columns, but no
        data row data.  We do it this way because get_empty_dataframe is more
        complicated for PdIntervalFrame.

        :return: DataFrame object
        """
        return self.frame_def.empty_dataframe


class PdIntervalFrameABC(PdFrameABC):
    """
    A PdFrame subclass for periodic data.  The class includes additional
    validation to ensure that the index is of timezone-aware datetimes with
    the expected periodicity.  The class also includes utility methods for
    periodic data.
    """

    def __init__(self, period, timezone, dataframe=None):
        """
        Creates a new PdIntervalFrame object.

        period will be internally stored as a Timedelta object.  However,
        it can be constructed with an integer number of seconds, a pandas
        frequency string, or a pandas Timedelta object.

        :param period: interval period expressed as one of the following:
            int - number of seconds,
            string - pandas frequency string (see https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html?highlight=frequency#dateoffset-objects)
            pandas Timedelta object
        :param timezone: pytz timezone object or timezone string
        :param dataframe: pandas DataFrame object
        """

        # Convert string to timezone object
        if type(timezone) == str:
            timezone = pytz.timezone(timezone)

        # Set metadata
        self.timezone = timezone
        self.period = get_period_as_timedelta(period)

        # Add in the frame_def and dataframe
        PdFrameABC.__init__(
            self,
            dataframe=dataframe
        )

    def validate(self, dataframe):
        """
        In addition to validating column types, validates:

        Dataframe index is a DateTimeIndex object
        Dataframe index dtype is Timestamp with correct Timezone
        DateTimeIndex frequency matches self.period

        :param dataframe:
        :return:
        """

        if super().validate(dataframe):
            # Dataframe passes column validation
            # Now validate index
            idx = dataframe.index

            if not isinstance(idx, pd.DatetimeIndex):
                # Index is not DatetimeIndex
                return False

            # Dtype should be datetime64 in the correct timezone
            dtype = pd.Series(
                dtype='datetime64[ns, {}]'.format(str(self.timezone))
            ).dtype
            if idx.dtype != dtype:
                # Incorrect dtype
                return False

            # Index frequency should match interval period.
            if idx.freq != self.period:
                return False

        return True

    def get_empty_dataframe(self):
        """
        Returns a properly formatted dataframe, with a correctly-formatted
        DateTimeIndex.

        :return: pandas DataFrame object
        """
        # Get dataframe with correctly formatted columns
        df = super().get_empty_dataframe()

        # Add DateTimeIndex
        idx = pd.DatetimeIndex(
            [],
            tz=self.timezone,
            freq=self.period,
            name='timestamp'
        )
        df.set_index(idx, inplace=True)

        return df
