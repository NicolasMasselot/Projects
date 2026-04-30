# Projects

Personal project collection.

## Projects

- [Carry Regime Compass](Carry-Regime-Compass/) - Python/Streamlit cross-asset carry-to-volatility monitor with Yahoo Finance data, SQLite caching, regime inference, and dashboard visualization.
- [Scribe](Scribe/) - Chrome extension that translates selected page text with a temporary visual overlay.

## Clone

Clone this repository with GitHub Desktop, then open the project you want from its folder.

For Carry Regime Compass:

```bash
cd Carry-Regime-Compass
pip install -e ".[dev]"
streamlit run carry_compass/viz/app.py
```

For Scribe, open the `Scribe` folder in Chrome using `chrome://extensions` > Developer mode > Load unpacked.
