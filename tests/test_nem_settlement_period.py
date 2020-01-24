"""Test the NemSettlementPeriod object."""
from datetime import date, datetime
from pytz import timezone
import pytest

from electric_units import NemSettlementPeriod


def test_can_create():
    """We can create a NemSettlementPeriod."""
    feb = datetime(2020, 2, 25, 12, 15, 12)
    set_per = NemSettlementPeriod(moment=feb)

    aest = timezone('Etc/GMT-10')

    assert set_per.start == aest.localize(datetime(2020, 2, 25, 12, 0, 0))
    assert set_per.end == aest.localize(datetime(2020, 2, 25, 12, 30, 0))
    assert set_per.start_date == date(2020, 2, 25)
    assert set_per.period_id == 25

    # Can handle change of days
    day_shift = datetime(2020, 2, 25, 23, 45, 12)
    set_per = NemSettlementPeriod(moment=day_shift)
    assert set_per.start == aest.localize(datetime(2020, 2, 25, 23, 30, 0))
    assert set_per.end == aest.localize(datetime(2020, 2, 26, 0, 0, 0))
    assert set_per.period_id == 48
    assert set_per.start_hour == 23
    assert set_per.end_hour == 0

    # Will convert a TZ aware datetime
    adelaide_tz = timezone('Australia/Adelaide')
    adelaide = adelaide_tz.localize(datetime(2020, 3, 23, 5, 34, 51))
    adelaide_sp = NemSettlementPeriod(moment=adelaide)
    assert adelaide_sp.start.isoformat() == '2020-03-23T05:00:00+10:00'


def test_can_create_from_string():
    """Can be created from a string."""
    set_per = NemSettlementPeriod(moment="2020-02-25T12:00:00")

    aest = timezone('Etc/GMT-10')
    assert set_per.start == aest.localize(datetime(2020, 2, 25, 12, 0, 0))


def test_can_compare():
    """Can compare two periods."""
    early = NemSettlementPeriod(datetime(2020, 2, 25, 12, 15, 12))
    late = NemSettlementPeriod(datetime(2020, 2, 26, 12, 15, 12))
    assert early < late

    # Same period
    assert NemSettlementPeriod(datetime(2020, 2, 25, 12, 15, 12)) == early
    # Same period, but instantiated one minute apart
    assert NemSettlementPeriod(datetime(2020, 2, 25, 12, 16, 12)) == early
    # Later period in an earlier day
    assert NemSettlementPeriod(datetime(2020, 2, 24, 14, 15, 12)) < early


NEM_DATA = [
    (
        '2020-02-02T00:15:00',
        timezone('Etc/GMT-10').localize(datetime(2020, 2, 2, 0, 0)),
        1
    ),
    (
        '2020-02-02T13:00:00',
        timezone('Etc/GMT-10').localize(datetime(2020, 2, 2, 13, 00)),
        27
    ),
    (
        '2020-02-02T13:33:00',
        timezone('Etc/GMT-10').localize(datetime(2020, 2, 2, 13, 30)),
        28
    ),
    (
        '2020-02-02T23:45:00',
        timezone('Etc/GMT-10').localize(datetime(2020, 2, 2, 23, 30)),
        48
    ),
]


@pytest.mark.parametrize("moment, start, period_id", NEM_DATA)
def test_nem_accuracy(moment, start, period_id):
    """Test the correct NEM period is built."""
    period = NemSettlementPeriod(moment)
    assert period.start == start
    assert period.period_id == period_id


def test_class_localize():
    """Can localize a datetie to match this class timezone."""
    naive = datetime(2019, 1, 1, 12, 00)
    localized_naive = NemSettlementPeriod.localize(naive).isoformat()
    assert localized_naive == "2019-01-01T12:00:00+10:00"

    utc_time = datetime(2019, 1, 1, 12, 00, tzinfo=timezone('UTC'))
    localized_utc_time = NemSettlementPeriod.localize(utc_time).isoformat()
    assert localized_utc_time == "2019-01-01T22:00:00+10:00"

    naive_str = "2019-01-01T12:00:00"
    localized_naive_str = NemSettlementPeriod.localize(naive_str).isoformat()
    assert localized_naive_str == "2019-01-01T12:00:00+10:00"

    utc_time_str = "2019-01-01T12:00:00Z"
    localized_utc_str = NemSettlementPeriod.localize(utc_time_str).isoformat()
    assert localized_utc_str == "2019-01-01T22:00:00+10:00"
