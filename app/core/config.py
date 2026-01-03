from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from app.core.returns import ReturnConfig


@dataclass(frozen=True)
class AppConfig:
    """Application-wide configuration."""
    tickers: list[str]
    years: int
    frequency: str
    threshold: float
    data_source: str
    uploaded_file: Optional[bytes] = None

    @property
    def threshold_pct(self) -> int:
        """Return threshold as percentage integer."""
        return int(self.threshold * 100)

    @property
    def return_config(self) -> ReturnConfig:
        """Get ReturnConfig from this config."""
        return ReturnConfig(frequency=self.frequency)

