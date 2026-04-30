import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from carry_compass.viz.theme import ASSET_CLASS_COLORS, REGIME_COLORS, REGIME_DESCRIPTIONS


def _format_pct(value: float, decimals: int = 1, signed: bool = False) -> str:
    sign = "+" if signed else ""
    return f"{value * 100:{sign}.{decimals}f}%"


def render_regime_banner(regime: str, carry_z: float, vol_z: float) -> None:
    """Render the single HTML-styled component: the current regime banner."""
    color = REGIME_COLORS.get(regime, "#334155")
    description = REGIME_DESCRIPTIONS.get(regime, "")
    st.markdown(
        f"""
        <div style="
            background: {color};
            color: white;
            padding: 18px 22px;
            border-radius: 6px;
            margin: 8px 0 18px 0;
            box-shadow: 0 1px 3px rgba(15, 23, 42, 0.16);
        ">
            <div style="
                font-size: 0.72rem;
                font-weight: 700;
                letter-spacing: 0.12em;
                text-transform: uppercase;
                opacity: 0.85;
            ">CURRENT REGIME</div>
            <div style="font-size: 1.9rem; font-weight: 760; line-height: 1.15;">
                {regime}
            </div>
            <div style="font-size: 0.95rem; margin-top: 6px; font-weight: 600;">
                Carry z = {carry_z:+.2f} &middot; Vol z = {vol_z:+.2f}
            </div>
            <div style="font-size: 0.92rem; margin-top: 8px; opacity: 0.92;">
                {description}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_kpis(
    latest: pd.DataFrame,
    panel: pd.DataFrame,
    n_tickers: int,
    stale_count: int,
) -> None:
    """Show compact operational context for the current dashboard state."""
    ratio_leader = latest.sort_values("ratio", ascending=False).iloc[0]
    median_ratio = latest["ratio"].median()
    date_count = panel["date"].nunique()
    summary = pd.DataFrame(
        [
            {
                "Latest assets": f"{len(latest)} / {n_tickers}",
                "Median carry/vol": f"{median_ratio:+.2f}",
                "Top signal": f"{ratio_leader['asset']} ({ratio_leader['ratio']:+.2f})",
                "Stale tickers": stale_count,
                "Panel dates": date_count,
            }
        ]
    )
    st.dataframe(summary, use_container_width=True, hide_index=True)


def render_scatter(latest: pd.DataFrame, centroid_trail: pd.DataFrame) -> None:
    """Render the carry/vol map and the 60-day macro centroid trail."""
    fig = px.scatter(
        latest,
        x="carry",
        y="vol",
        color="asset_class",
        color_discrete_map=ASSET_CLASS_COLORS,
        hover_name="asset",
        hover_data={
            "asset": True,
            "asset_class": True,
            "ratio": ":.2f",
            "carry": ":.4f",
            "vol": ":.3f",
        },
    )
    fig.update_traces(marker={"size": 12, "line": {"color": "white", "width": 1}})

    if not centroid_trail.empty:
        trail = centroid_trail.reset_index().rename(columns={"index": "date"})
        denom = max(len(trail) - 1, 1)
        marker_sizes = [4 + 6 * (idx / denom) for idx in range(len(trail))]
        fig.add_trace(
            go.Scatter(
                x=trail["carry_med"],
                y=trail["vol_med"],
                mode="lines+markers",
                name="Centroid trail",
                line={"color": "rgba(0,0,0,0.45)", "dash": "dot", "width": 2},
                marker={"size": marker_sizes, "color": "rgba(0,0,0,0.45)"},
                customdata=trail["date"],
                hovertemplate="Centroid %{customdata|%Y-%m-%d}<br>"
                "Carry=%{x:.4f}<br>Vol=%{y:.3f}<extra></extra>",
            )
        )
        today = trail.iloc[-1]
        fig.add_trace(
            go.Scatter(
                x=[today["carry_med"]],
                y=[today["vol_med"]],
                mode="markers",
                name="Centroid (today)",
                marker={"size": 18, "color": "black", "symbol": "x"},
                customdata=[today["date"]],
                hovertemplate="Today %{customdata|%Y-%m-%d}<br>"
                "Carry=%{x:.4f}<br>Vol=%{y:.3f}<extra></extra>",
            )
        )

    fig.update_layout(
        height=540,
        template="plotly_white",
        xaxis_title="Carry (annualized, decimal)",
        yaxis_title="Realized vol (annualized, decimal)",
        legend_title="Asset class",
        hovermode="closest",
        margin={"l": 10, "r": 10, "t": 10, "b": 10},
        font={"size": 13},
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "left",
            "x": 0,
        },
    )
    fig.update_xaxes(
        tickformat=".0%",
        zeroline=True,
        zerolinecolor="#94a3b8",
        gridcolor="#e5e7eb",
    )
    fig.update_yaxes(
        tickformat=".0%",
        zeroline=True,
        zerolinecolor="#94a3b8",
        gridcolor="#e5e7eb",
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def render_table(latest: pd.DataFrame) -> None:
    """Render the current cross-section sorted by raw carry-to-vol ratio."""
    show = latest.sort_values("ratio", ascending=False).copy()
    show = show[["asset", "asset_class", "carry", "vol", "ratio"]]
    show["carry"] = show["carry"].map(lambda x: _format_pct(x, decimals=2, signed=True))
    show["vol"] = show["vol"].map(lambda x: _format_pct(x, decimals=1))
    show["ratio"] = show["ratio"].map(lambda x: f"{x:+.2f}")
    show = show.rename(
        columns={
            "asset": "Asset",
            "asset_class": "Class",
            "carry": "Carry",
            "vol": "Vol",
            "ratio": "Carry/Vol",
        }
    )
    st.dataframe(show, use_container_width=True, hide_index=True)


def render_transitions(transitions: list[object]) -> None:
    """Render recent confirmed regime transitions as a small audit table."""
    if not transitions:
        st.caption("No confirmed transitions in the last 120 trading days.")
        return

    rows = [
        {
            "Confirmed": transition.confirmed_at,
            "From": transition.from_regime.value,
            "To": transition.to_regime.value,
        }
        for transition in transitions[-5:]
    ]
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
