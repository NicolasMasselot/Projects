from concurrent.futures import ThreadPoolExecutor, as_completed

from loguru import logger

from carry_compass.config import load_config
from carry_compass.data.fetcher import DataFetcher, FetchResult


def fetch_universe(force_refresh: bool = False, max_workers: int = 4) -> dict[str, FetchResult]:
    cfg = load_config()
    fetcher = DataFetcher()
    results: dict[str, FetchResult] = {}

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(fetcher.fetch_history, asset.ticker, None, force_refresh): asset.ticker
            for asset in cfg.universe
        }
        for future in as_completed(futures):
            ticker = futures[future]
            try:
                results[ticker] = future.result()
            except Exception as exc:
                logger.exception("unrecoverable fetch error for {}: {}", ticker, exc)

    return results
