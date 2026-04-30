import pandas as pd

from carry_compass.carry.aggregate import compute_all_carries
from carry_compass.config import load_config
from carry_compass.vol.realized import compute_all_vols

PANEL_COLS = ["date", "asset", "asset_class", "carry", "vol", "ratio"]
MAX_RATIO_ABS = 19.999


def _label_to_asset_class() -> dict[str, str]:
    cfg = load_config()
    label_to_class = {asset.label: asset.asset_class.value for asset in cfg.universe}
    for asset in cfg.universe:
        if asset.ticker.endswith("=X"):
            body = asset.ticker.replace("=X", "")
            label_to_class[f"{body[:3]}/{body[3:]}"] = asset.asset_class.value
    return label_to_class


def _stack_metric(frame: pd.DataFrame, name: str) -> pd.DataFrame:
    return (
        frame.stack(future_stack=True)
        .rename(name)
        .reset_index()
        .rename(columns={"level_0": "date", "level_1": "asset"})
    )


def build_carry_vol_panel(prices: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Build a tidy carry/volatility panel.

    Carry and realized volatility are restricted to common asset labels and common
    dates before stacking. The raw ratio is carry divided by realized volatility,
    with zero-vol rows dropped, then winsorized to keep extreme low-vol carry trades
    from dominating the unified monitor. The output is long format for regime and
    visualization layers.
    """
    label_to_class = _label_to_asset_class()
    carry = compute_all_carries(prices)
    vol = compute_all_vols(prices)
    if carry.empty or vol.empty:
        return pd.DataFrame(columns=PANEL_COLS)

    common_cols = carry.columns.intersection(vol.columns)
    common_dates = carry.index.intersection(vol.index)
    if common_cols.empty or common_dates.empty:
        return pd.DataFrame(columns=PANEL_COLS)

    carry = carry.loc[common_dates, common_cols]
    vol = vol.loc[common_dates, common_cols]

    c_long = _stack_metric(carry, "carry")
    v_long = _stack_metric(vol, "vol")
    panel = c_long.merge(v_long, on=["date", "asset"], how="inner")
    panel["asset_class"] = panel["asset"].map(label_to_class)
    panel["ratio"] = panel["carry"].divide(panel["vol"].replace(0, pd.NA))
    panel = panel.dropna(subset=["carry", "vol", "ratio"])
    panel["ratio"] = panel["ratio"].clip(-MAX_RATIO_ABS, MAX_RATIO_ABS)
    return panel[PANEL_COLS]
