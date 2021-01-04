import pandas as pd

import pandjas.exceptions as exc


def get_period_as_timedelta(period):
    """
    Takes as input either an integer number of seconds, a pandas frequency
    string, or a pandas Timedelta object.  Converts input to a pandas
    Timedelta object.

    :param period: int # of seconds, str pandas frequency string, or Timedelta
    :return: pandas Timedelta object
    """
    if isinstance(period, int):
        # Convert seconds to Timedelta.
        period = pd.Timedelta('{}s'.format(period))

    elif isinstance(period, str):
        # Convert pandas frequency string.
        try:
            period = pd.Timedelta(period)
        except ValueError:
            # Must be valid frequency string
            raise exc.InvalidIntervalPeriodError()

    elif not isinstance(period, pd.Timedelta):
        # Must be a Timedelta then.
        raise exc.InvalidIntervalPeriodError()

    return period
