class PandjasErrorMixin(Exception):
    """
    Mixin for providing all exceptions with default messages and codes
    """
    def __init__(self, message=None):
        self.message = message if message else self.default_detail

    def __str__(self):
        return self.message

    @property
    def default_detail(self):
        raise NotImplementedError()

    @property
    def default_code(self):
        raise NotImplementedError()


class NoColumnDefNameError(PandjasErrorMixin, Exception):
    default_detail = "All columns definitions must include a name."
    default_code = "objects_no_column_def_name"

class DuplicateColumnDefNameError(PandjasErrorMixin, Exception):
    default_detail = "A column name is being used more than once."
    default_code = "objects_duplicate_column_def_name"

class NoColumnDefFileDefError(PandjasErrorMixin, Exception):
    default_detail = "All columns definitions must include a file_def."
    default_code = "objects_no_column_def_file_def"


class IllegalDtypeStringError(PandjasErrorMixin, Exception):
    default_detail = "Incorrect string for identifying column dtype"
    default_code = "objects_illegal_dtypes_string"


class InvalidDataFrameError(PandjasErrorMixin, Exception):
    default_detail = "Dataframe does not meet formatting expectations."
    default_code = "objects_invalid_dataframe"


class InvalidIntervalPeriodError(PandjasErrorMixin, Exception):
    default_detail = "Period must either be an int number of seconds, a " \
                     "pandas frequency string, or a pandas Timedelta object."
    default_code = "objects_invalid_interval_period"
