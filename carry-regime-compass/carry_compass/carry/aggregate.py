import pandas as pd

from carry_compass.carry.commodity import compute_commodity_carry
from carry_compass.carry.credit import compute_credit_carry
from carry_compass.carry.equity import compute_equity_carry
from carry_compass.carry.fx import compute_fx_carry
from carry_compass.carry.rates import compute_rates_carry


def compute_all_carries(prices: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Aggregate all asset-class carry estimates into one date x asset-label frame.

    Each component returns annualized decimal carry. Concatenation preserves each
    asset class's explicit date alignment; downstream cross-asset aggregation should
    use medians rather than means because high-carry markets such as TRY can dominate.
    """
    parts = [
        compute_fx_carry(prices),
        compute_rates_carry(prices),
        compute_credit_carry(prices),
        compute_equity_carry(prices),
        compute_commodity_carry(prices),
    ]
    parts = [part for part in parts if not part.empty]
    if not parts:
        return pd.DataFrame()
    return pd.concat(parts, axis=1).sort_index()
