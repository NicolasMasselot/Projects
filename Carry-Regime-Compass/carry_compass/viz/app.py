import datetime as dt

import streamlit as st
from streamlit_autorefresh import st_autorefresh

from carry_compass.config import load_config
from carry_compass.data.batch import fetch_universe
from carry_compass.regime.centroid import compute_centroid
from carry_compass.regime.classifier import regime_timeseries
from carry_compass.regime.transitions import detect_transitions, smoothed_regime
from carry_compass.utils.logging import configure_logging
from carry_compass.vol.panel import build_carry_vol_panel
from carry_compass.viz.components import (
    render_kpis,
    render_regime_banner,
    render_scatter,
    render_table,
    render_transitions,
)

st.set_page_config(page_title="Carry Regime Compass", layout="wide")


def _regime_label(value: object) -> str:
    return str(getattr(value, "value", value))


@st.cache_data(ttl=120, show_spinner="Fetching universe...")
def _load_panel(force: bool = False):
    res = fetch_universe(force_refresh=force)
    prices = {ticker: result.df for ticker, result in res.items() if not result.df.empty}
    panel = build_carry_vol_panel(prices)
    centroid = compute_centroid(panel)
    regimes = regime_timeseries(centroid)
    regimes["regime_smoothed"] = smoothed_regime(regimes)
    return panel, centroid, regimes, res


def main() -> None:
    configure_logging()
    cfg = load_config()
    st_autorefresh(interval=cfg.refresh_seconds * 1000, key="auto_refresh_tick")

    with st.sidebar:
        st.header("Controls")
        force = st.button("Force refresh", help="Bypass cache and request fresh Yahoo data.")
        st.divider()
        st.subheader("Universe")
        st.caption(
            f"Universe: {len(cfg.universe)} tickers · "
            f"{len({asset.asset_class for asset in cfg.universe})} asset classes"
        )
        st.caption(f"Vol window: {cfg.vol.window_days} bdays")
        st.caption(f"Smoothing: {cfg.regime.transition_smoothing_days} days")
        st.caption(f"Auto-refresh: {cfg.refresh_seconds // 60} min")

    if force:
        _load_panel.clear()
    panel, centroid, regimes, fetch_results = _load_panel(force=force)

    if panel.empty or regimes.empty:
        st.error("No data available. Check logs/carry_compass.log.")
        return

    last_date = panel["date"].max()
    latest = panel[panel["date"] == last_date]
    last_regime_row = regimes.iloc[-1]
    current_regime = _regime_label(
        last_regime_row.get("regime_smoothed") or last_regime_row["regime"]
    )
    stale = sum(1 for result in fetch_results.values() if result.stale)

    st.title("Carry Regime Compass")
    st.caption(
        "Cross-asset carry-to-volatility monitor · Yahoo Finance · "
        f"latest panel date {last_date.strftime('%Y-%m-%d')}"
    )
    render_regime_banner(current_regime, last_regime_row["carry_z"], last_regime_row["vol_z"])
    render_kpis(latest, panel, len(fetch_results), stale)

    col1, col2 = st.columns([3, 2])
    with col1:
        st.subheader("Carry vs realized volatility")
        st.caption("Current cross-section with the 60-day median carry/vol centroid trail.")
        trail = centroid.tail(60)[["carry_med", "vol_med"]]
        render_scatter(latest, trail)
    with col2:
        st.subheader("Asset ranking")
        st.caption("Sorted by carry-to-volatility ratio, descending.")
        render_table(latest)

    st.subheader("Recent regime transitions")
    transitions = detect_transitions(regimes.tail(120))
    render_transitions(transitions)

    st.caption(
        f"Last refresh: {dt.datetime.now().strftime('%H:%M:%S')} · "
        f"{len(fetch_results)} tickers fetched · {stale} served from stale cache"
    )


if __name__ == "__main__":
    main()
