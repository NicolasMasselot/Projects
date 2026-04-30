ASSET_CLASS_COLORS = {
    "fx_carry": "#2563eb",
    "rates": "#ea580c",
    "credit": "#16a34a",
    "equity": "#dc2626",
    "commodity": "#7c3aed",
}

REGIME_COLORS = {
    "Risk-On": "#15803d",
    "Mid-Cycle": "#0369a1",
    "Late-Cycle": "#b45309",
    "Deleveraging": "#b91c1c",
}

REGIME_DESCRIPTIONS = {
    "Risk-On": (
        "Cross-asset carry is rich, realized volatility is depressed. "
        "Classic carry-friendly environment."
    ),
    "Mid-Cycle": "Carry and vol both near long-run averages. No strong directional signal.",
    "Late-Cycle": (
        "Carry still rich but vol is creeping up. Watch for crowded carry trades."
    ),
    "Deleveraging": (
        "Vol spike with depressed carry. Risk-off, fund-the-bid, USD bid environment."
    ),
}
