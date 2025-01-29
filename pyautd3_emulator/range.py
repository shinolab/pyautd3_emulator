from typing import Self

from pyautd3_emulator.native_methods.autd3capi_emulator import RangeXYZ as RangeXYZ_


class RangeXYZ:
    _inner: RangeXYZ_

    def __init__(
        self: Self,
        *,
        x_start: float,
        x_end: float,
        y_start: float,
        y_end: float,
        z_start: float,
        z_end: float,
        resolution: float,
    ) -> None:
        self._inner = RangeXYZ_(
            x_start,
            x_end,
            y_start,
            y_end,
            z_start,
            z_end,
            resolution,
        )
