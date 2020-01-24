"""A SettlementPeriod in the NEM region."""
from datetime import timedelta
from pytz import timezone
from attr import attrs

from electric_units.base_settlement_period import BaseSettlementPeriod


@attrs(frozen=True)
class NemSettlementPeriod(BaseSettlementPeriod):
    """A NEM Settlement Period.

    NEM has 30 minute periods. Instantiate one with a moment in time.
    This will assume this moment is in AEST timezone, or, if a Timezone is
    present in the instantiating moment, then it will be converted to AEST.

    Args:
        moment: A datetime, or None to use the current time.
    """

    @property
    def freq_minutes(self):
        """The NEM has 30 minute periods."""
        return 30

    @staticmethod
    def time_zone():
        """Australian Eastern Standard Time."""
        return timezone('Etc/GMT-10')

    @property
    def start(self):
        """Rewind to the start of the half hour."""
        moment = self.tz_match(self.moment)

        mins = moment.minute
        if mins < 30:
            round_by = mins
        else:
            round_by = (30 - mins) * -1

        start = moment - timedelta(minutes=round_by)
        start = start.replace(second=0, microsecond=0)
        return start

    def _period_id(self):
        """An integer representing the AEMO Period ID within the day."""
        start_time = self.start.time()
        hour = start_time.hour
        period_id = (hour * 2) + 1

        minute = start_time.minute
        if minute >= 30:
            period_id = period_id + 1

        return period_id
