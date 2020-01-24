"""Pandas DType and Array for NemSettlementPeriod."""
import sys
import numpy as np

from pandas.api.extensions import register_extension_dtype, take
from pandas.api.types import is_list_like, is_scalar
from pandas.core.arrays import ExtensionArray
from pandas.core.dtypes.base import ExtensionDtype


from electric_units.nem_settlement_period import NemSettlementPeriod


@register_extension_dtype
class NemSettlementPeriodDtype(ExtensionDtype):
    """A custom data type, to be paired with an ExtensionArray."""

    type = NemSettlementPeriod
    name = "nem_settlement_period"

    @classmethod
    def construct_array_type(cls):
        """Return the array type associated with this dtype."""
        return NemSettlementPeriodArray


class NemSettlementPeriodArray(ExtensionArray):
    """Abstract base class for custom 1-D array types."""

    def __init__(self, values, dtype=NemSettlementPeriodDtype, copy=False):
        """Instantiate the array."""
        if copy:
            values = values.copy()
        if not isinstance(values[0], NemSettlementPeriod):
            values = [NemSettlementPeriod(val) for val in values]
        self.data = np.asarray(values, dtype=object)
        self._dtype = dtype()

    def __setitem__(self, key, value):
        """Set one or more values inplace."""
        if is_list_like(value):
            if is_scalar(key):
                raise ValueError("setting an array element with a sequence.")
            value = [NemSettlementPeriod(val) for val in value]
        else:
            value = NemSettlementPeriod(value)
        self.data[key] = value

    @classmethod
    def _from_sequence(cls, scalars, dtype=None, copy=False):
        """Construct a new ExtensionArray from a sequence of scalars."""
        return cls(scalars)

    @classmethod
    def _from_factorized(cls, values, original):
        """Reconstruct an ExtensionArray after factorization."""
        values = [val.decode('utf-8') for val in values]
        return cls(values)

    def _values_for_factorize(self):
        """Factorize to the ISO8601, with TZ, of the start datetime."""
        starts = np.fromiter((s.start.isoformat() for s in self), '|S25')
        return np.array(starts, dtype=object, copy=True), np.nan

    def __getitem__(self, item):
        """Select a subset of self."""
        return self.data[item]

    def __len__(self):
        """Length of this array."""
        return len(self.data)

    @property
    def nbytes(self):
        """The byte size of the data."""
        return len(self) * sys.getsizeof(self[0])

    @property
    def dtype(self):
        """An instance of 'ExtensionDtype'."""
        return self._dtype

    def isna(self):
        """A 1-D array indicating if each value is missing."""
        return np.array([False for x in self.data], dtype=bool)

    def take(self, indices, allow_fill=False, fill_value=None):
        """Take elements from an array.

        Relies on the take method defined in pandas:
        https://github.com/pandas-dev/pandas/blob/e246c3b05924ac1fe083565a765ce847fcad3d91/pandas/core/algorithms.py#L1483
        """
        data = self.data
        if allow_fill and fill_value is None:
            fill_value = self.dtype.na_value

        result = take(
            data, indices, fill_value=fill_value, allow_fill=allow_fill)
        return self._from_sequence(result)

    def copy(self):
        """Return a copy of the array."""
        return type(self)(self.data.copy())

    @classmethod
    def _concat_same_type(cls, to_concat):
        """Concatenate multiple arrays."""
        return cls(np.concatenate([x.data for x in to_concat]))
