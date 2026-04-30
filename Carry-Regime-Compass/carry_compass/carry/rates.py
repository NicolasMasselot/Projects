import pandas as pd

from carry_compass.config import load_config
from carry_compass.config.schema import AssetClass


def compute_rates_carry(prices: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Term premium proxy: long yield - 3M yield.

    Yahoo rates are quoted in percent, so this function divides by 100 and returns
    decimal annualized carry. This is a yield-curve proxy, not realized bond carry
    including duration, roll-down, or financing mechanics.
    """
    if "^IRX" not in prices:
        raise ValueError("rates carry requires ^IRX in prices")

    cfg = load_config()
    short = prices["^IRX"]["close"] / 100.0
    out: dict[str, pd.Series] = {}
    for asset in cfg.universe:
        if asset.asset_class != AssetClass.RATES or asset.role != "primary":
            continue
        if asset.ticker not in prices:
            continue
        long_y = prices[asset.ticker]["close"] / 100.0
        common = long_y.index.intersection(short.index)
        out[asset.label] = long_y.loc[common] - short.loc[common]

    return pd.DataFrame(out).sort_index()
