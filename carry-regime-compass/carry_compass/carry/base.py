from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class CarryResult:
    asset_class: str
    df: pd.DataFrame


def safe_div(a: pd.Series, b: pd.Series) -> pd.Series:
    return a.divide(b.replace(0, pd.NA))
