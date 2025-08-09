from __future__ import annotations

import time
import uuid
from typing import List
from datetime import datetime

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import pyperclip

from .sheets import SheetsClient


def log_app(client: SheetsClient, event: str, details: str, status: str, notes: str, run_id: str) -> None:
    client.log_row(
        content=f"Auto Poster {event}",
        post_type="App Message",
        details=details,
        status=status,
        notes=notes,
        run_id=run_id,
    )


def post_to_group(driver, wait: WebDriverWait, client: SheetsClient, group_url: str, text: str, image_paths: List[str], run_id: str) -> bool:
    driver.get(group_url)
    try:
        selectors = [
            "//span[contains(text(), 'Write something...')]",
            "//span[contains(text(), \"What's on your mind\")]",
            "//div[@role='button']//span[contains(text(), 'Write something')]",
            "//div[contains(@class, 'x1lliihq')]//span[contains(text(), 'Write something')]",
        ]
        create_post_input = None
        for sel in selectors:
            try:
                create_post_input = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, sel)))
                break
            except Exception:
                continue
        if not create_post_input:
            raise RuntimeError("Create-post input not found")
        create_post_input.click()

        # text area
        text_area_selectors = [
            "//div[@role='textbox' and @contenteditable='true' and @aria-placeholder='Create a public post…']",
            "//div[@role='textbox' and @contenteditable='true' and @aria-placeholder='Write something...']",
            "//div[@role='textbox' and @contenteditable='true' and contains(@aria-placeholder, 'Write something')]",
            "//div[@role='textbox' and @contenteditable='true' and contains(@aria-placeholder, 'Create a public post')]",
        ]
        text_area = None
        for sel in text_area_selectors:
            try:
                text_area = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, sel)))
                break
            except Exception:
                continue
        if not text_area:
            raise RuntimeError("Text area not found")
        text_area.click()
        pyperclip.copy(text)
        text_area.send_keys(Keys.CONTROL + 'v')
        time.sleep(2)

        photo_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Photo/video' and @role='button']")))
        # climb and find file input
        parent = photo_btn
        for _ in range(3):
            parent = parent.find_element(By.XPATH, './..')
        file_input = parent.find_element(By.XPATH, ".//input[@type='file' and starts-with(@accept, 'image')]")
        file_input.send_keys("\n".join(image_paths))

        post_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Post' and @role='button']")))
        time.sleep(5)
        post_button.click()

        posting_wait = WebDriverWait(driver, 120)
        posting_el = posting_wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Posting')]")))
        posting_wait.until(EC.invisibility_of_element(posting_el))

        client.log_row(
            content=(text[:50] + "...") if len(text) > 50 else text,
            post_type="Group post",
            details=f"Posted to {group_url}",
            status="Posted",
            notes=f"Images: {len(image_paths)}",
            run_id=run_id,
        )
        return True
    except Exception as e:
        client.log_row(
            content=(text[:50] + "...") if len(text) > 50 else text,
            post_type="Group post",
            details=f"Failed to post to {group_url}",
            status="Error",
            notes=f"Error: {e}",
            run_id=run_id,
        )
        return False

