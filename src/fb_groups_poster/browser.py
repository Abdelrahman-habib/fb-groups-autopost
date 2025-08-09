from __future__ import annotations

from selenium import webdriver
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.edge.service import Service
from webdriver_manager.microsoft import EdgeChromiumDriverManager

from .config import BrowserConfig


def build_edge(cfg: BrowserConfig) -> webdriver.Edge:
    opts = EdgeOptions()
    opts.use_chromium = True
    opts.add_argument(f"user-data-dir={cfg.edge_profile_dir}")
    opts.add_argument(f"profile-directory={cfg.edge_profile_name}")
    service = Service(EdgeChromiumDriverManager(
        url="https://msedgedriver.microsoft.com/",
        latest_release_url="https://msedgedriver.microsoft.com/LATEST_RELEASE",
    ).install())
    return webdriver.Edge(service=service, options=opts)

