import numpy as np
import pandas as pd


def compute_commodity_carry(prices: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Commodity roll/cost-of-carry approximations.

    WTI uses (CL=F - BZ=F) / CL=F * 12 as a cross-grade proxy for a longer-dated
    crude contract; this is not a real CL2-CL1 spread, so the proxy is bounded to
    +/-99.9% to avoid cross-grade dislocations overwhelming the monitor. Gold
    carry is -3M T-bill yield as a funding cost proxy. Copper uses six-month log
    return annualized as a poor-man's term-structure proxy because Yahoo lacks
    clean futures curves.
    """
    out: dict[str, pd.Series] = {}
    if "CL=F" in prices and "BZ=F" in prices:
        cl = prices["CL=F"]["close"]
        bz = prices["BZ=F"]["close"]
        common = cl.index.intersection(bz.index)
        out["WTI front"] = (((cl.loc[common] - bz.loc[common]) / cl.loc[common]) * 12.0).clip(
            -0.999, 0.999
        )
    if "GC=F" in prices and "^IRX" in prices:
        rf = prices["^IRX"]["close"] / 100.0
        common = prices["GC=F"].index.intersection(rf.index)
        out["Gold"] = -rf.reindex(common)
    if "HG=F" in prices:
        cu = prices["HG=F"]["close"]
        out["Copper"] = np.log(cu / cu.shift(126)) * 2.0

    return pd.DataFrame(out).sort_index()
