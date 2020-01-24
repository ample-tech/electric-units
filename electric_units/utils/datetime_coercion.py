"""Convert from a string to a datetime."""

from dateutil.parser import parse


def datetime_coercion(moment):
    """Force the return of a datetime object."""
    if isinstance(moment, str):
        return parse(moment)
    return moment
