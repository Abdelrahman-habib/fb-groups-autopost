from __future__ import annotations

import uuid
from datetime import datetime
from typing import Dict

from selenium.webdriver.support.ui import WebDriverWait
import click
import logging
import time
import os
from .cli_ui import Spinner
from tqdm import tqdm

from .config import AppConfig
from .browser import build_edge
from .sheets import init_sheets, get_filtered_group_links
from .poster import post_to_group, log_app


def run_posting(cfg: AppConfig, assume_yes: bool = False) -> bool:
    logger = logging.getLogger(__name__)
    # Silence Selenium / urllib3 noise unless verbose logging is enabled
    if logging.getLogger().level > logging.DEBUG:
        for noisy in (
            "selenium",
            "urllib3",
            "WDM",  # webdriver-manager
        ):
            logging.getLogger(noisy).setLevel(logging.WARNING)
        # Also silence Selenium driver manager stdout if possible
        os.environ.setdefault("WDM_LOG_LEVEL", "0")
    # Stage: Initialize Sheets
    sp = Spinner("Initializing Google Sheets client")
    sp.start()
    try:
        sheets = init_sheets(cfg.sheets)
        sp.succeed()
    except Exception as e:
        sp.fail("failed to initialize")
        logger.exception("Failed to initialize Google Sheets client: %s", e)
        click.echo("Check your service account file, spreadsheet ID, and sharing permissions.", err=True)
        return False

    # Stage: Fetch groups
    tags_label = ", ".join(cfg.poster.filter_tags) or "<none>"
    sp = Spinner(f"Fetching group links (tags: {tags_label})")
    sp.start()
    try:
        group_links = get_filtered_group_links(sheets, cfg.poster.filter_tags) or []
        sp.succeed(f"  —  {len(group_links)} group(s)")
    except Exception as e:
        sp.fail("failed to fetch groups")
        logger.exception("Failed to fetch group links: %s", e)
        return False
    count = len(group_links)
    if count == 0:
        click.echo("No groups matched the provided filter tags. Nothing to post.")
        return False
    if not assume_yes and not click.confirm(f"Proceed to post to {count} group(s)?", default=True):
        click.echo("Aborted by user before posting.")
        return False

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

    # Stage: Launch browser
    sp = Spinner(f"Launching Edge (headless={getattr(cfg.browser, 'headless', False)})")
    sp.start()
    try:
        driver = build_edge(cfg.browser)
        wait = WebDriverWait(driver, 60)
        sp.succeed()
    except Exception as e:
        sp.fail("failed to launch browser")
        logger.exception("Failed to launch browser: %s", e)
        return False

    logger.info("Browser ready. Starting posting run: %s", run_id)

    success = 0
    errors = 0
    try:
        total = len(group_links)
        click.echo("")
        with tqdm(total=total, desc="Posting to groups", unit="group", ncols=80) as pbar:
            for idx, url in enumerate(group_links, start=1):
                iter_start = time.time()
                ok = post_to_group(driver, wait, sheets, url, cfg.poster.text, cfg.poster.image_paths, run_id)
                elapsed = time.time() - iter_start
                symbol = "✅" if ok else "❌"
                if ok:
                    success += 1
                else:
                    errors += 1
                pbar.set_postfix({"last": f"{elapsed:.1f}s", "ok": success, "err": errors})
                pbar.update(1)
                click.echo(f"  {symbol} [{idx}/{total}] {elapsed:.1f}s  {url}")
    finally:
        logger.info("Shutting down browser…")
        driver.quit()
        duration = str(datetime.now() - start_time).split('.')[0]
        status = "Finished" if errors == 0 else f"Finished, Error ({errors} errors)"
        logger.info("Run complete in %s. Success: %d, Errors: %d", duration, success, errors)
        log_app(
            sheets,
            event="Finished",
            details=f"Completed. Success: {success}, Errors: {errors}",
            status=status,
            notes=f"Total: {len(group_links)}; Duration: {duration}",
            run_id=run_id,
        )

    return errors == 0

