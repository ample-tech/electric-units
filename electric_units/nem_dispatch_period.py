"""A SettlementPeriod in the NEM region."""
from datetime import timedelta
from pytz import timezone
from attr import attrs

from electric_units.base_settlement_period import BaseSettlementPeriod


@attrs(frozen=True)
class NemDispatchPeriod(BaseSettlementPeriod):
    """A NEM Dispatch Period.

    The NEM is operated with 5-minute dispatch periods.
    Instantiate one with a moment in time. This will assume this moment is
    in AEST timezone, or, if a Timezone is present in the instantiating moment,
    then it will be converted to AEST.

    Args:
        moment: A datetime, or None to use the current time.
    """

    @property
    def freq_minutes(self):
        """A dispatch period is 5 minutes long"""
        return 5

    @staticmethod
    def time_zone():
        """Australian Eastern Standard Time."""
        return timezone('Etc/GMT-10')

    @property
    def start(self):
        """Rewind to the start of the 5-minute period."""
        moment = self.tz_match(self.moment)

        delta_to_start = timedelta(minutes=moment.minute % 5,
                                   seconds=moment.second,
                                   microseconds=moment.microsecond)

        start = moment - delta_to_start
        return start

    def _period_id(self):
        """An integer representing the dispatch period in the day.
        Ranges from 1 to 288, and resets to 1 at 4:00AM AEST"""
        if self.start.hour < 4:
            hour = self.start.hour + 20 # 20 hours from 4:00 to midnight
        else:
            hour = self.start_hour - 4
        minute = self.start.minute

        period_id = (12 * hour) + int(minute / 5) + 1

        return period_id

    @property
    def dispatch_interval(self):
        """String representing the unique interval, DISPATCHINTERVAL in the 
        NEM data. Takes the form of a zero-padded date string with a 
        period ID at the end. Each day starts at 4:00AM AEST"""
        start = self.start
        start_date = start.date()

        # add zero padding to make period_id 3 chars long
        period_id = str(self.period_id).zfill(3)

        if start.hour < 4 and period_id != "001":
            start_date = start_date - timedelta(days=1)

        # Concat zero-padded dates and add period id
        dispatch_interval = "".join([start_date.strftime("%Y%m%d"), period_id])

        return dispatch_interval
