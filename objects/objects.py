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

    def __init__(self):

        self.column_defs = dict()

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
