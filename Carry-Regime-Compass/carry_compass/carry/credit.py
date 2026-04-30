from functools import lru_cache

import pandas as pd
import yfinance as yf
from loguru import logger

FALLBACK_YIELDS = {"HYG": 0.065, "LQD": 0.045, "IEF": 0.040}


@lru_cache(maxsize=32)
def _ticker_dividend_yield(ticker: str, fallback: float) -> float:
    try:
        info = yf.Ticker(ticker).info
        raw = info.get("yield") or info.get("dividendYield")
        logger.debug("{} raw dividend yield from yfinance: {}", ticker, raw)
        if raw is None:
            return fallback
        value = float(raw)
        if value > 1:
            value /= 100.0
        return value
    except Exception as exc:
        logger.warning("failed to fetch dividend yield for {}: {}", ticker, exc)
        return fallback


def compute_credit_carry(prices: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """HY/IG ETF distribution yield minus IEF yield.

    Distribution yield is fetched once via yf.Ticker(...).info and applied as a
    constant across the historical window. In production we'd use OAS spreads from
    ICE BofA indices rather than ETF distribution yields.
    """
    if "IEF" not in prices:
        raise ValueError("credit carry requires IEF in prices")

    ief_index = prices["IEF"].index
    ief_yield = _ticker_dividend_yield("IEF", FALLBACK_YIELDS["IEF"])
    out: dict[str, pd.Series] = {}
    for ticker, label in (("HYG", "HY ETF"), ("LQD", "IG ETF")):
        if ticker not in prices:
            continue
        common = prices[ticker].index.intersection(ief_index)
        yld = _ticker_dividend_yield(ticker, FALLBACK_YIELDS[ticker])
        out[label] = pd.Series(yld - ief_yield, index=common, dtype="float64")

    return pd.DataFrame(out).sort_index()
