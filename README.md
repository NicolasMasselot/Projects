# Projects

Personal project collection.

## Projects

- **Scribe** - Chrome extension that translates selected page text with a temporary visual overlay.
- **Carry Regime Compass** - Python/Streamlit dashboard built for a Python for Finance course. It tracks whether cross-asset carry is being sufficiently rewarded for realized volatility across FX, rates, credit, equities, and commodities, then classifies the current macro regime as Risk-On, Mid-Cycle, Late-Cycle, or Deleveraging.

## Clone

Clone this repository with GitHub Desktop, then open the project you want from its folder.

For Carry Regime Compass:

```bash
cd "Carry Regime Compass"
pip install -e ".[dev]"
streamlit run carry_compass/viz/app.py
```

For Scribe, open the `Scribe` folder in Chrome using `chrome://extensions` > Developer mode > Load unpacked.
