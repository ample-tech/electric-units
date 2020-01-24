"""Test the datetime coercion."""

from datetime import datetime
from pytz import timezone
from electric_units.utils.datetime_coercion import datetime_coercion


def test_datetime():
    """Handle a datetime input."""
    moment = datetime(2020, 2, 25, 12, 15, 0)
    assert moment == datetime_coercion(moment)

    aest = timezone('Etc/GMT-10')
    aest_moment = aest.localize(datetime(2020, 2, 25, 12, 0, 0))
    assert aest_moment == datetime_coercion(aest_moment)


def test_string_input():
    """Handle a string input."""
    moment = datetime(2020, 2, 25, 12, 15, 0)
    moment_as_string = moment.isoformat()
    assert moment == datetime_coercion(moment_as_string)

    aest = timezone('Etc/GMT-10')
    aest_moment = aest.localize(datetime(2020, 2, 25, 12, 0, 0))
    aest_moment_as_string = aest_moment.isoformat()
    assert aest_moment == datetime_coercion(aest_moment_as_string)
