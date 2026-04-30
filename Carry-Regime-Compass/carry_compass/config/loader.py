from functools import lru_cache
from pathlib import Path

import yaml

from carry_compass.config.schema import AppConfig

DEFAULT_CONFIG_PATH = Path(__file__).parent / "universe.yaml"


@lru_cache(maxsize=1)
def load_config(path: Path | None = None) -> AppConfig:
    p = path or DEFAULT_CONFIG_PATH
    with p.open("r") as f:
        raw = yaml.safe_load(f)
    return AppConfig(**raw)
