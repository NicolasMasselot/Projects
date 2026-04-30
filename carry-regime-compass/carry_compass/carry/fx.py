import pandas as pd

SHORT_RATES_PROXY = {
    "USD": 0.0500,
    "EUR": 0.0250,
    "JPY": 0.0050,
    "CHF": 0.0100,
    "GBP": 0.0475,
    "AUD": 0.0410,
    "NZD": 0.0475,
    "CAD": 0.0450,
    "BRL": 0.1175,
    "MXN": 0.1025,
    "TRY": 0.4500,
    "ZAR": 0.0775,
}
EM_FUNDED = {"USDBRL=X", "USDMXN=X", "USDTRY=X", "USDZAR=X"}


def _decode_fx_ticker(ticker: str) -> tuple[str, str]:
    body = ticker.replace("=X", "")
    return body[:3], body[3:]


def compute_fx_carry(prices: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Interest-rate differential proxy for FX carry.

    This is not true forward-point or FX-swap carry; it uses indicative central-bank
    short-rate proxies held constant across the historical window. Sign convention:
    for USDxxx EM pairs we report the carry of being LONG xxx vs SHORT USD, the
    standard carry trade. For all other pairs, carry is long FX1 vs short FX2.
    """
    out: dict[str, pd.Series] = {}
    for ticker, df in prices.items():
        if not ticker.endswith("=X") or len(ticker.replace("=X", "")) != 6 or df.empty:
            continue
        c1, c2 = _decode_fx_ticker(ticker)
        r1 = SHORT_RATES_PROXY.get(c1)
        r2 = SHORT_RATES_PROXY.get(c2)
        if r1 is None or r2 is None:
            continue
        carry = (r2 - r1) if ticker in EM_FUNDED else (r1 - r2)
        out[f"{c1}/{c2}"] = pd.Series(carry, index=df.index, dtype="float64")

    return pd.DataFrame(out).sort_index()
