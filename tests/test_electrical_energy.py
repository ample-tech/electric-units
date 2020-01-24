"""Test the ElectricalEnergy object."""
import pytest

from electric_units import ElectricalEnergy, NemSettlementPeriod, WattSample
from electric_units.electrical_energy import (
    _extrapolate_constant, _average_kwh, TooFewSamples)


def test_simple_create():
    """Can create an energy object from power samples."""
    energy = ElectricalEnergy(
        kwh=2, start='2019-11-01T13:30:00', end='2019-11-01T13:35:00')

    assert energy.kwh == 2.0
    assert energy.time == 5 * 60
    assert energy.samples is None


def test_create_from_two_power_samples():
    """Can create an energy object from 2 power samples."""
    sample_1 = WattSample(watts=1000, moment='2019-11-01T13:30:00')
    sample_2 = WattSample(watts=10000, moment='2019-11-01T13:00:00')

    energy = ElectricalEnergy.from_power_samples([sample_1, sample_2])

    assert energy.start == sample_2.moment
    assert energy.end == sample_1.moment

    assert energy.kwh == 2.75

    assert energy.samples[0] == sample_2
    assert energy.samples[1] == sample_1

    # Is the same as the energy object created without explicit samples.
    assert energy == ElectricalEnergy(
        kwh=2.75, start='2019-11-01T13:00:00', end='2019-11-01T13:30:00')


def test_create_from_multiple_power_samples():
    """Can create an energy object, weighting multiple power samples."""
    sample_1 = WattSample(watts=30000, moment='2019-11-01T13:00:00')
    sample_2 = WattSample(watts=60000, moment='2019-11-01T13:20:00')
    sample_3 = WattSample(watts=72000, moment='2019-11-01T13:30:00')

    samples = [sample_1, sample_2, sample_3]

    energy = ElectricalEnergy.from_power_samples(samples)

    assert energy.samples[0] == sample_1
    assert energy.samples[1] == sample_2
    assert energy.samples[2] == sample_3
    assert len(energy.samples) == len(samples)

    assert energy.kwh == 26.0


def test_settlement_periods():
    """Can report the periods within the energy use."""
    energy = ElectricalEnergy(
        kwh=1, start='2019-11-01T09:00:00', end='2019-11-01T11:30:00')

    periods = energy.settlement_periods(NemSettlementPeriod)
    # 09:00 -> 09:30
    # 09:30 -> 10:00
    # 10:00 -> 10:30
    # 10:30 -> 11:00
    # 11:00 -> 11:30
    assert len(periods) == 5


def test_aggregation_by_period_from_start_end_creation():
    """An energy object, simply created, can be aggregated by period."""
    energy = ElectricalEnergy(
        kwh=10, start='2019-11-01T09:00:00', end='2019-11-01T11:30:00')

    energy_periods = energy.by_period(NemSettlementPeriod)
    assert len(energy_periods) == 5
    for energy_period in energy_periods:
        assert energy_period.kwh == 2


def test_iteration():
    """We should be able to iterate over the object."""
    energy = ElectricalEnergy(
        kwh=2, start='2019-11-01T13:30:00', end='2019-11-01T13:35:00')
    energy_dict = [s.__dict__ for s in [energy]]
    assert energy_dict[0]['kwh'] == 2


def test_aggregation_by_period_from_samples():
    """An energy object, created from samples, can be aggregated by period."""
    sample_1_1 = WattSample(watts=10000, moment='2019-11-01T13:00:00')
    sample_2_1 = WattSample(watts=10000, moment='2019-11-01T13:30:00')
    sample_2_2 = WattSample(watts=20000, moment='2019-11-01T13:45:00')
    sample_3_1 = WattSample(watts=10000, moment='2019-11-01T14:05:00')
    sample_3_2 = WattSample(watts=30000, moment='2019-11-01T14:15:00')
    samples = [sample_1_1, sample_2_1, sample_2_2, sample_3_1, sample_3_2]

    energy = ElectricalEnergy.from_power_samples(samples)

    # Energy between 13:00 and 14:15 is of a varied nature.
    #
    #   1. 30min constant 10kW
    #   2. 15min varying from 10 to 20 kW (average 15)
    #   3. 20min varying from 20 to 10 kW (average 15)
    #   4. 10min varying from 10 to 30 kW (average 20)
    # Total:
    #   Approx 17.083333 kWh over 1hr 15min (75min)
    assert energy.kwh == 5 + 3.75 + 5 + (20 * (10 / 60))
    assert energy.time == 75 * 60

    energy_periods = energy.by_period(NemSettlementPeriod)
    assert len(energy_periods) == 3

    # FIRST PERIOD:
    periods_1 = energy_periods[0].settlement_periods(NemSettlementPeriod)
    assert len(periods_1) == 1
    assert periods_1 == [NemSettlementPeriod('2019-11-01T13:00:00')]
    #   Constant power of 10kW across the 30min, measured only at the start
    assert energy_periods[0].kwh == 5.0
    assert len(energy_periods[0].samples) == 2

    # SECOND PERIOD:
    periods_2 = energy_periods[1].settlement_periods(NemSettlementPeriod)
    assert len(periods_2) == 1
    assert periods_2 == [NemSettlementPeriod('2019-11-01T13:30:00')]
    #   1. Power rises from 10 to 20 (mean 15kW) in first 15min
    #   2. Implied constant 20kW for the remaining 15min
    assert energy_periods[1].kwh == (15 * (15 / 60)) + (20 * (15 / 60))
    assert len(energy_periods[1].samples) == 3

    # THIRD PERIOD:
    periods_3 = energy_periods[2].settlement_periods(NemSettlementPeriod)
    assert len(periods_3) == 1
    assert periods_3 == [NemSettlementPeriod('2019-11-01T14:00:00')]
    #   1. Initial 5min is constant 10kW
    #   2. Power rises from 10 to 30 (mean 20 kW) over the next 10min
    #   3. Constant power of 30kW for the final 15min
    # Total:
    #   Approx 11.6667 across the 30min
    expeted_period_3 = (10 * (5 / 60)) + (20 * (10 / 60)) + (30 * (15 / 60))
    assert energy_periods[2].kwh == expeted_period_3
    assert len(energy_periods[2].samples) == 4


PERIOD_DATA = [
    (
        '2019-11-01T13:30:00',
        '2019-11-01T13:35:00',
        [
            NemSettlementPeriod('2019-11-01T13:30:00')
        ]
    ),
    (
        '2019-11-01T13:30:00',
        '2019-11-01T14:25:00',
        [
            NemSettlementPeriod('2019-11-01T13:30:00'),
            NemSettlementPeriod('2019-11-01T14:00:00')
        ]
    ),
    (
        '2019-11-01T13:00:00',
        '2019-11-01T14:35:00',
        [
            NemSettlementPeriod('2019-11-01T13:00:00'),
            NemSettlementPeriod('2019-11-01T13:30:00'),
            NemSettlementPeriod('2019-11-01T14:00:00'),
            NemSettlementPeriod('2019-11-01T14:30:00'),
        ]
    )

]


@pytest.mark.parametrize("start_moment, end_moment, periods", PERIOD_DATA)
def test_periods(start_moment, end_moment, periods):
    """Report which periods this energy is within."""
    energy = ElectricalEnergy(kwh=2, start=start_moment, end=end_moment)
    assert energy.settlement_periods(NemSettlementPeriod) == periods


def test_constant_exrapolation():
    """Extrapolate a power rating to an earlier or later time."""
    to_time = '2019-01-01T00:00:00'
    power_rating = 10000
    sample = WattSample(watts=10000, moment='2019-11-01T13:00:00')

    assert _extrapolate_constant(to_time, sample) == WattSample(
        watts=power_rating, moment=to_time)


def test_average_kwh():
    """Test the calculation of a weighted average energy."""
    samples = [
        WattSample(watts=10000, moment='2019-11-01T13:00:00'),
        WattSample(watts=5000, moment='2019-11-01T13:30:00')
    ]
    assert _average_kwh(samples) == 7.5 / 2
    with pytest.raises(TooFewSamples):
        _average_kwh([samples[0]])
