from enum import Enum

import pandas as pd

from carry_compass.config import load_config
from carry_compass.config.schema import RegimeThresholds


class Regime(str, Enum):
    RISK_ON = "Risk-On"
    MID_CYCLE = "Mid-Cycle"
    LATE_CYCLE = "Late-Cycle"
    DELEVERAGING = "Deleveraging"


def classify_row(carry_z: float, vol_z: float, t: RegimeThresholds) -> Regime:
    if vol_z >= t.deleveraging_vol_z_min and carry_z <= t.deleveraging_carry_z_max:
        return Regime.DELEVERAGING
    if carry_z >= t.risk_on_carry_z_min and vol_z <= t.risk_on_vol_z_max:
        return Regime.RISK_ON
    if carry_z >= 0 and vol_z > t.risk_on_vol_z_max:
        return Regime.LATE_CYCLE
    return Regime.MID_CYCLE


def regime_timeseries(centroid: pd.DataFrame) -> pd.DataFrame:
    cfg = load_config()
    regimes = centroid.copy()
    regimes["regime"] = [
        classify_row(row.carry_z, row.vol_z, cfg.regime)
        for row in regimes[["carry_z", "vol_z"]].itertuples(index=False)
    ]
    return regimes
