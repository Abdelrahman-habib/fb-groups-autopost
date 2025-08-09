from __future__ import annotations

from selenium import webdriver
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.edge.service import Service
from webdriver_manager.microsoft import EdgeChromiumDriverManager

from .config import BrowserConfig
import os


def build_edge(cfg: BrowserConfig) -> webdriver.Edge:
    opts = EdgeOptions()
    opts.use_chromium = True
    opts.add_argument(f"user-data-dir={cfg.edge_profile_dir}")
    opts.add_argument(f"profile-directory={cfg.edge_profile_name}")
    # Reduce browser / driver noise in console
    opts.add_experimental_option("excludeSwitches", ["enable-logging"])  # suppress "DevTools listening" line
    opts.add_argument("--log-level=3")
    if getattr(cfg, "headless", False):
        # Use new headless mode; ensure a reasonable window size for layout-dependent selectors
        opts.add_argument("--headless=new")
        opts.add_argument("--disable-gpu")
        opts.add_argument("--window-size=1920,1080")
    driver_path = EdgeChromiumDriverManager(
        url="https://msedgedriver.microsoft.com/",
        latest_release_url="https://msedgedriver.microsoft.com/LATEST_RELEASE",
    ).install()
    # Suppress webdriver service logs regardless of Selenium version
    try:
        service = Service(driver_path, log_output=os.devnull, service_args=['--log-level=OFF'])  # Selenium >= 4.25
    except TypeError:
        service = Service(driver_path, log_path=os.devnull)    # Older Selenium
    return webdriver.Edge(service=service, options=opts)

