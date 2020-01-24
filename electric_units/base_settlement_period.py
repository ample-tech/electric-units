"""A base SettlementPeriod class to build market specific periods from."""

from datetime import datetime, timedelta
from attr import attrs, attrib

from electric_units.utils.datetime_coercion import datetime_coercion


@attrs(frozen=True)
class BaseSettlementPeriod:
    """A Settlement Period.

    Settlement periods have a duration, exist in a timezone, and
    a means of expressing the period as an integer within a day.

    Args:
        moment: A datetime, or None to use the current time.
    """

    moment = attrib(converter=datetime_coercion, eq=False, repr=False)
    start_date = attrib(init=False, type=datetime)
    period_id = attrib(init=False, type=int)

    def __attrs_post_init__(self):
        """Post hook from attrs."""
        object.__setattr__(self, "period_id", self._period_id())
        object.__setattr__(self, "start_date", self._start_date())

    @property
    def freq_minutes(self):
        """Must be set to the region specific period duration."""
        raise NotImplementedError

    @staticmethod
    def time_zone():
        """The default timezone for this region's periods."""
        raise NotImplementedError

    @property
    def timezone(self):
        """Pull the timezone into a property of the class."""
        return self.__class__.time_zone()

    @property
    def end(self):
        """A Datetime object for the moment at the end of the period."""
        return self.start + timedelta(minutes=self.freq_minutes)

    def _start_date(self):
        """The Date the period started on."""
        return self.start.date()

    @property
    def end_date(self):
        """The Date thee period ended on."""
        return self.end.date()

    @property
    def start_hour(self):
        """An integer - the hour the period started on."""
        return self.start.hour

    @property
    def end_hour(self):
        """An integer - the hour the period ended on."""
        return self.end.hour

    def _period_id(self):
        """An integer representing the AEMO Period ID."""
        raise NotImplementedError

    @moment.default
    # pylint: disable=no-self-use
    def default_moment(self):
        """Default to UTC now."""
        return datetime.utcnow()

    @property
    def start(self):
        """A Datetime object for the moment at the start of the period.

        This object is instantiated with a moment, round this moment down
        to the start of the period.
        """
        raise NotImplementedError

    def tz_match(self, moment):
        """Localize the instantiaing moment to match this period."""
        return self.__class__.localize(moment)

    @classmethod
    def localize(cls, moment):
        """Localize a date time to match this period."""
        time_zone = cls.time_zone()

        dt_moment = datetime_coercion(moment)
        if dt_moment.tzinfo is not None:
            return dt_moment.astimezone(time_zone)
        return time_zone.localize(dt_moment)
