"""Are the units usable within pandas."""
from pandas import DataFrame, Series

from electric_units.pandas_compat import NemSettlementPeriodArray


def test_pandas_entension():
    """Can you built a series with the settlement period."""
    periods = NemSettlementPeriodArray([
        '2019-01-01T10:00:00',
        '2019-01-01T11:00:00',
        '2019-01-01T12:00:00',
        '2019-01-01T12:10:00',
    ])

    series = Series(periods)
    assert series[0].period_id == 21
    assert series[0].start_hour == 10
    assert series[2] != series[1]
    assert series[2] == series[3]
    assert series.dtype == 'nem_settlement_period'


def test_type_declaration():
    """String name of the DType can be used to instantiate a Series."""
    series = Series(['2019-01-01T10:00:00', '2019-01-01T12:00:00'],
                    dtype="nem_settlement_period")
    assert series.dtype == 'nem_settlement_period'
    assert series[0].period_id == 21


def test_group_by_period_id():
    """Can you take an average of data within the same period."""
    data = DataFrame({
        "prices": [10, 20, 80, 40],
        "datetimes": NemSettlementPeriodArray([
            '2019-01-02T10:01:00',
            '2019-01-02T10:05:00',
            '2019-01-02T11:00:00',
            '2019-01-02T11:10:00',
        ])
    })

    assert data.groupby('datetimes').prices.mean()[0] == 15
    assert data.groupby('datetimes').prices.mean()[1] == 60
