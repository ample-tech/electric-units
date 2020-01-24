"""Test the WattSample object."""

from datetime import datetime
from pytz import timezone
import pytest

from electric_units import NemSettlementPeriod, WattSample


def test_can_create():
    """We can create a power sample."""
    adelaide_tz = timezone('Australia/Adelaide')
    sample_time = adelaide_tz.localize(datetime(2020, 3, 23, 5, 34, 51))
    power_sample = WattSample(watts=1000, moment=sample_time)
    assert power_sample.killowatts == 1
    assert power_sample.megawatts == 0.001

    sample_period = power_sample.settlement_period(NemSettlementPeriod)
    period = NemSettlementPeriod(moment=sample_time)
    assert sample_period == period


def test_can_create_from_string():
    """Can create a power sample from a string."""
    sample = WattSample(watts=1000, moment="2020-01-01T00:30:00")
    assert sample.moment == datetime(2020, 1, 1, 0, 30)


SP_DATA = [
    ('2020-01-01T12:05:00', '2020-01-01T12:00:00'),
    ('2020-01-01T12:35:00', '2020-01-01T12:30:00'),
    ('2020-01-01T13:00:00', '2020-01-01T13:00:00'),
    ('2020-01-01T13:30:00', '2020-01-01T13:30:00'),
    ('2020-01-01T13:35:00', '2020-01-01T13:30:00'),
]


@pytest.mark.parametrize("sample_momemt, period_moment", SP_DATA)
def test_settlement_period(sample_momemt, period_moment):
    """Test that it reports the correct SP."""
    sample = WattSample(watts=1, moment=sample_momemt)
    period = NemSettlementPeriod(period_moment)
    assert sample.settlement_period(NemSettlementPeriod) == period


def test_can_compare():
    """We can compare the size of two samples.

    Should compare the size of the power, not the time the sample was taken.
    """
    early = datetime.utcnow()
    late = datetime.utcnow()

    assert late > early

    small = WattSample(watts=1000, moment=late)
    large = WattSample(watts=10000, moment=early)
    largest = WattSample(watts=100000, moment=early)

    assert small < large
    assert large < largest
    assert small == WattSample(watts=1000, moment=late)
    assert small != WattSample(watts=1000, moment=early)
