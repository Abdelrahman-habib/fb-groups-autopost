from dataclasses import dataclass, field
from typing import List, Optional
import os
import yaml


@dataclass
class SheetsConfig:
    service_account_file: str
    spreadsheet_id: str
    tracker_sheet: str = "auto-poster-tracker"
    groups_sheet: str = "Groups"


@dataclass
class BrowserConfig:
    edge_profile_dir: str
    edge_profile_name: str = "Default"


@dataclass
class PosterConfig:
    text: str
    image_paths: List[str]
    filter_tags: List[str] = field(default_factory=list)


@dataclass
class AppConfig:
    sheets: SheetsConfig
    browser: BrowserConfig
    poster: PosterConfig


def load_config(path: str) -> AppConfig:
    with open(path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    sheets = SheetsConfig(**raw["sheets"])
    browser = BrowserConfig(**raw["browser"])
    poster = PosterConfig(**raw["poster"])

    # Normalize paths
    sheets.service_account_file = os.path.abspath(sheets.service_account_file)
    poster.image_paths = [os.path.abspath(p) for p in poster.image_paths]

    return AppConfig(sheets=sheets, browser=browser, poster=poster)

