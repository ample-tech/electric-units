"""An amount of energy."""

from collections import defaultdict
from statistics import mean
from attr import attrs, attrib

from electric_units.utils.datetime_coercion import datetime_coercion


@attrs(frozen=True)
class ElectricalEnergy:
    """Energy used within a period of time."""

    kwh = attrib(type=float)
    start = attrib(converter=datetime_coercion)
    end = attrib(converter=datetime_coercion)
    samples = attrib(type=list, eq=False, repr=False, default=None)

    @classmethod
    def from_power_samples(cls, samples):
        """Create the energy object from a list of power samples.

        The energy is the weighted average of the power.

        The time between 2 samples creates a weight for the power,
        and the power being drawn between those 2 samples is the mean of those
        2 power samples.
        """
        if len(samples) < 2:
            raise TooFewSamples

        sorted_samples = sorted(samples, key=lambda sample: sample.moment)

        earliest = sorted_samples[0]
        latest = sorted_samples[-1]

        kwh = _average_kwh(sorted_samples)
        return cls(kwh=kwh,
                   start=earliest.moment, end=latest.moment,
                   samples=sorted_samples)

    @property
    def time(self):
        """Time of work, in seconds."""
        duration = self.end - self.start
        return duration.seconds

    def by_period(self, period_class):
        """Summarise the energy use in each whole settlement period."""
        if self.samples is None:
            return self._spread_energy_across_sps(period_class)

        grouped_power_samples = self._get_samples_by_period(period_class)

        energy_groups = []
        for period, p_samples in grouped_power_samples.items():
            p_samples = sorted(p_samples, key=lambda sample: sample.moment)

            first_sample = p_samples[0]
            last_sample = p_samples[-1]

            if period.tz_match(first_sample.moment) > period.start:
                start_extra = _extrapolate_constant(period.start, first_sample)
                p_samples.insert(0, start_extra)

            if period.tz_match(last_sample.moment) < period.end:
                end_extra = _extrapolate_constant(period.end, last_sample)
                p_samples.append(end_extra)

            period_energy = self.from_power_samples(p_samples)
            energy_groups.append(period_energy)

        return energy_groups

    def settlement_periods(self, period_class):
        """The periods within which this energy is used."""
        periods = []
        first_period = period_class(self.start)
        periods.append(first_period)

        while periods[-1].end < periods[-1].tz_match(self.end):
            new_period = period_class(periods[-1].end)
            periods.append(new_period)

        return periods

    def _spread_energy_across_sps(self, period_class):
        """Apply a constant mean power to all SPs within the time bound."""
        energy_groups = []
        settlement_periods = self.settlement_periods(period_class)
        mean_period_energy = self.kwh / len(settlement_periods)
        for period in settlement_periods:
            period_energy = self.__class__(
                kwh=mean_period_energy, start=period.start, end=period.end)
            energy_groups.append(period_energy)
        return energy_groups

    def _get_samples_by_period(self, period_class):
        """Return a dict, keys are the period, values are a list of samples."""
        power_groups = defaultdict(list)
        for sample in self.samples:
            sample_period = sample.settlement_period(period_class)
            tz_moment = sample_period.tz_match(sample.moment)
            tz_sample = sample.__class__(watts=sample.watts, moment=tz_moment)
            power_groups[sample_period].append(tz_sample)
        return power_groups

    def __iter__(self):
        """Iterable."""
        for key in ['kwh', 'start']:
            yield getattr(self, key)


def _extrapolate_constant(to_time, from_sample):
    """Extrapolate a power rating to an earlier or later time.

    This models a constant power rating before (or after)
    the `from_sample` input to the `to_time`.

    It returns a power sample, of the same class as the `from_sample`
    but at the time specified in `to_time`.
    """
    sample_class = from_sample.__class__
    watts = from_sample.watts
    extrapolated_sample = sample_class(watts=watts, moment=to_time)
    return extrapolated_sample


def _average_kwh(power_samples):
    """Average khw of a group of samples."""
    if len(power_samples) < 2:
        raise TooFewSamples

    kwh = 0
    for sample_1, sample_2 in zip(power_samples[:-1], power_samples[1:]):
        watts = mean([sample_1.watts, sample_2.watts])
        duration = (sample_2.moment - sample_1.moment).seconds
        kwh += (watts / 1000) * (duration / 3600)

    return kwh


class TooFewSamples(IndexError):
    """There are not enough power sampels to represent an energy."""
