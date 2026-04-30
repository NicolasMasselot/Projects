import numpy as np
import pandas as pd

from carry_compass.config import load_config

YIELD_TICKERS = {"^IRX", "^FVX", "^TNX", "^TYX"}


def _is_yield_ticker(ticker: str) -> bool:
    return ticker in YIELD_TICKERS


def realized_vol(
    series: pd.Series,
    window: int = 30,
    annualization: int = 252,
    min_obs: int = 20,
    is_yield: bool = False,
) -> pd.Series:
    """Compute annualized realized volatility.

    Price branch: sigma_t = sqrt(252) * stdev(ln(P_t / P_{t-1}) over window).
    Yield branch: sigma_t = sqrt(252) * stdev(delta Y_t in decimal over window).
    The yield branch avoids log returns because yields can be near zero or negative.
    """
    clean = pd.to_numeric(series, errors="coerce")
    if is_yield:
        rets = (clean / 100.0).diff()
    else:
        rets = np.log(clean / clean.shift(1))
    vol = rets.rolling(window=window, min_periods=min_obs).std(ddof=1)
    return vol * np.sqrt(annualization)


def compute_all_vols(prices: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Compute annualized realized volatility for all configured assets.

    Output columns use configured asset labels so they align with the carry layer.
    Yahoo yield tickers use decimal yield changes; all other assets use price log
    returns. This is backward-looking realized volatility, not implied volatility.
    """
    cfg = load_config()
    out: dict[str, pd.Series] = {}
    for asset in cfg.universe:
        frame = prices.get(asset.ticker)
        if frame is None or frame.empty:
            continue
        out[asset.label] = realized_vol(
            frame["close"],
            window=cfg.vol.window_days,
            annualization=cfg.vol.annualization_factor,
            min_obs=cfg.vol.min_observations,
            is_yield=_is_yield_ticker(asset.ticker),
        )
    return pd.DataFrame(out).sort_index()
