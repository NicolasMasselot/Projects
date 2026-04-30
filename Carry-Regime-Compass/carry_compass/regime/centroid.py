import pandas as pd


def compute_centroid(panel: pd.DataFrame) -> pd.DataFrame:
    """Compute the cross-asset macro centroid in carry/vol space.

    Step 1: cross-sectional median of carry and vol per date, robust to outliers.
    Step 2: z-score those two median time series over their available history.

    Returns a date-indexed frame with columns:
    [carry_med, vol_med, carry_z, vol_z, n_assets].
    """
    daily = (
        panel.groupby("date")
        .agg(
            carry_med=("carry", "median"),
            vol_med=("vol", "median"),
            n_assets=("asset", "count"),
        )
        .sort_index()
    )

    carry_std = daily["carry_med"].std(ddof=1)
    vol_std = daily["vol_med"].std(ddof=1)
    daily["carry_z"] = (daily["carry_med"] - daily["carry_med"].mean()) / carry_std
    daily["vol_z"] = (daily["vol_med"] - daily["vol_med"].mean()) / vol_std
    return daily[["carry_med", "vol_med", "carry_z", "vol_z", "n_assets"]]
