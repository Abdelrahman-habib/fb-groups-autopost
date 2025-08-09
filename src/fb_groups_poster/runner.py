from __future__ import annotations

import uuid
from datetime import datetime
from typing import Dict

from selenium.webdriver.support.ui import WebDriverWait

from .config import AppConfig
from .browser import build_edge
from .sheets import init_sheets, get_filtered_group_links
from .poster import post_to_group, log_app


def run_posting(cfg: AppConfig) -> bool:
    sheets = init_sheets(cfg.sheets)
    group_links = get_filtered_group_links(sheets, cfg.poster.filter_tags) or []

    run_id = str(uuid.uuid4())
    start_time = datetime.now()

    log_app(
        sheets,
        event="Started",
        details=f"Starting for {len(group_links)} groups",
        status="Started",
        notes=f"Tags: {', '.join(cfg.poster.filter_tags)}; Images: {len(cfg.poster.image_paths)}",
        run_id=run_id,
    )

    driver = build_edge(cfg.browser)
    wait = WebDriverWait(driver, 60)

    success = 0
    errors = 0
    try:
        for url in group_links:
            ok = post_to_group(driver, wait, sheets, url, cfg.poster.text, cfg.poster.image_paths, run_id)
            if ok:
                success += 1
            else:
                errors += 1
    finally:
        driver.quit()
        duration = str(datetime.now() - start_time).split('.')[0]
        status = "Finished" if errors == 0 else f"Finished, Error ({errors} errors)"
        log_app(
            sheets,
            event="Finished",
            details=f"Completed. Success: {success}, Errors: {errors}",
            status=status,
            notes=f"Total: {len(group_links)}; Duration: {duration}",
            run_id=run_id,
        )

    return errors == 0

