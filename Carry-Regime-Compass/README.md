# Carry Regime Compass

Carry Regime Compass is a Python and Streamlit dashboard for monitoring cross-asset
carry opportunities against realized volatility, then classifying the current macro
environment into an interpretable regime.

The app pulls Yahoo Finance market data, stores normalized OHLCV history in a local
SQLite cache, computes annualized carry and realized volatility across asset classes,
and renders a professional dashboard for regime monitoring.

## What It Does

- Tracks a 26-ticker universe across FX carry, rates, credit, equity, and commodities.
- Fetches live Yahoo Finance data with retry/backoff and a SQLite-backed cache.
- Computes annualized carry in decimal form for each asset class.
- Computes rolling realized volatility with separate logic for price assets and yield series.
- Builds a tidy carry/vol panel with carry-to-volatility ratios.
- Infers macro regimes from the cross-asset median carry/vol centroid.
- Smooths regime transitions to avoid noisy day-to-day flicker.
- Displays the current regime, carry/vol scatter, centroid trail, asset ranking, and recent transitions in Streamlit.

## Regime Framework

The regime classifier maps the cross-asset carry/vol centroid into four states:

- **Risk-On**: carry is rich and realized volatility is low.
- **Mid-Cycle**: carry and vol are close to their own long-run averages.
- **Late-Cycle**: carry is still rich, but volatility is rising.
- **Deleveraging**: volatility spikes while carry is depressed.

The centroid is deliberately robust: it first takes the daily cross-sectional median
of carry and volatility, then z-scores those median time series through history.
This avoids the common mistake of averaging same-day cross-sectional z-scores, which
would mechanically collapse toward zero.

## Project Structure

```text
carry_compass/
  cache/      SQLite schema, DAO, and cache CLI
  config/     Pydantic config models and universe.yaml
  data/       Yahoo Finance fetching, normalization, batch loading
  carry/      Per-asset-class carry models and aggregate carry frame
  vol/        Realized volatility and carry/vol panel construction
  regime/     Centroid, classifier, transition smoothing
  viz/        Streamlit dashboard components and app entrypoint
tests/        Unit and integration tests
```

## Install

Requires Python `>=3.11,<3.13`.

```bash
pip install -e ".[dev]"
```

## Run The Dashboard

```bash
streamlit run carry_compass/viz/app.py
```

The dashboard auto-refreshes every five minutes by default. The interval is configured
in `carry_compass/config/universe.yaml` via `refresh_seconds`.

## Useful Commands

Initialize the cache:

```bash
python -m carry_compass.cache.cli init
```

Fetch one ticker:

```bash
python -m carry_compass.data.cli fetch ^GSPC
```

Fetch the full universe:

```bash
python -m carry_compass.data.cli fetch-all
```

Show cache statistics:

```bash
python -m carry_compass.cache.cli stats
```

Run tests and lint:

```bash
pytest
ruff check carry_compass tests
```

## Important Modeling Notes

- All carry values are annualized decimals: `0.045` means `4.5%`.
- Yahoo rates such as `^IRX`, `^TNX`, and `^TYX` are quoted in percent and converted only in the carry/vol layers.
- FX carry uses indicative short-rate differentials, not true FX forward points or swap-implied carry.
- Credit carry uses ETF distribution-yield approximations; a production-grade version would use OAS spread series.
- Equity carry uses trailing P/E snapshots as an earnings-yield proxy; production systems would use historical earnings-yield time series.
- Commodity carry uses pragmatic Yahoo-compatible proxies because clean futures curves are not available from Yahoo Finance.

## Current Scope

This is a research and monitoring tool, not a trading system. It is designed to make
cross-asset carry conditions easier to inspect, compare, and discuss.
