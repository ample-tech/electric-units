"""A measurement or power at a given time."""

from attr import attrs, attrib

from electric_units.utils.datetime_coercion import datetime_coercion


@attrs(frozen=True)
class WattSample:
    """A sample of the power being drawn.

    A measurement, in watts, of electrical power being
    drawn at a specific moment in time.
    """

    watts = attrib(type=float)
    moment = attrib(converter=datetime_coercion)

    def settlement_period(self, period_class):
        """The period which this sample was taken within."""
        return period_class(moment=self.moment)

    @property
    def killowatts(self):
        """Convenience for more common scale of measurement - Killowatts."""
        return self.watts / 1000

    @property
    def megawatts(self):
        """Convenience for more common scale of measurement - Megawatts."""
        return self.killowatts / 1000
