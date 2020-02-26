"""Test the NemDispatchPeriod object. Assumes that the base object is the
same as the NemSettlementPeriod object, so it doesn't require the same tests"""
from datetime import datetime
from pytz import timezone
import pytest

from electric_units import NemDispatchPeriod

NEM_DATA = [
    (
        '2019-10-01T03:59:00',
        timezone('Etc/GMT-10').localize(datetime(2019, 10, 1, 3, 55)),
        288,
        "20190930288"
    ),
    (
        '2019-10-01T04:00:00',
        timezone('Etc/GMT-10').localize(datetime(2019, 10, 1, 4, 0)),
        1,
        "20191001001"
    ),
    (
        '2019-10-01T04:07:00',
        timezone('Etc/GMT-10').localize(datetime(2019, 10, 1, 4, 5)),
        2,
        "20191001002"
    ),
    (
        '2019-10-01T23:55:00',
        timezone('Etc/GMT-10').localize(datetime(2019, 10, 1, 23, 55)),
        240,
        "20191001240"
    ),
    (
        '2019-10-01T00:00:00',
        timezone('Etc/GMT-10').localize(datetime(2019, 10, 1, 0, 0)),
        241,
        "20190930241"
    ),
]

@pytest.mark.parametrize("moment, start, period_id, dispatch_interval", NEM_DATA)
def test_nem_accuracy(moment, start, period_id, dispatch_interval):
    """Test the correct NEM period is built."""
    period = NemDispatchPeriod(moment)
    assert period.start == start
    assert period.period_id == period_id
    assert period.dispatch_interval == dispatch_interval
	