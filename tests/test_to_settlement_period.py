"""Are the units usable within pandas."""
from pandas import Series

from electric_units.pandas_compat import NemSettlementPeriodArray as PeriodType
from electric_units.pandas_compat import to_settlement_period


def test_pandas_entension():
    """Can you convert a series of strings to settlement periods."""
    series_of_strings = Series([
        '2019-01-01T10:00:00',
        '2019-01-01T11:00:00',
    ])
    series_of_periods = to_settlement_period(PeriodType, series_of_strings)

    print(series_of_periods.dtype)
    assert series_of_periods.dtype == 'nem_settlement_period'
