from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os


@dataclass(frozen=True)
class Settings:
    root_dir: Path = Path(__file__).resolve().parents[1]
    app_env: str = os.getenv("APP_ENV", "development")
    cmapss_data_dir: Path = Path(os.getenv("CMAPSS_DATA_DIR", "data/raw/CMAPSSData"))
    ims_data_dir: Path = Path(os.getenv("IMS_DATA_DIR", "data/raw/IMS"))
    rul_model_path: Path = Path(os.getenv("RUL_MODEL_PATH", "models/cmapss_fd001_rul.joblib"))
    max_fleet_assets: int = int(os.getenv("MAX_FLEET_ASSETS", "12"))

    @property
    def frontend_dir(self) -> Path:
        return self.root_dir / "frontend"

    @property
    def sample_dir(self) -> Path:
        return self.root_dir / "data" / "sample"

    def resolve(self, path: Path) -> Path:
        return path if path.is_absolute() else self.root_dir / path


settings = Settings()
