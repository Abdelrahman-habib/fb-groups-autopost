from __future__ import annotations

from typing import List, Tuple
from dataclasses import dataclass
from datetime import datetime

import gspread
from google.oauth2.service_account import Credentials

from .config import SheetsConfig


SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


@dataclass
class SheetsClient:
    tracker_ws: any
    groups_ws: any

    def log_row(self, content: str, post_type: str, details: str, status: str, notes: str, run_id: str) -> None:
        self.tracker_ws.append_row([
            content,
            post_type,
            details,
            status,
            datetime.now().strftime("%m/%d/%Y %H:%M:%S"),
            notes,
            run_id,
        ])


def init_sheets(cfg: SheetsConfig) -> SheetsClient:
    creds = Credentials.from_service_account_file(cfg.service_account_file, scopes=SCOPES)
    client = gspread.authorize(creds)
    ss = client.open_by_key(cfg.spreadsheet_id)
    tracker = ss.worksheet(cfg.tracker_sheet)
    groups = ss.worksheet(cfg.groups_sheet)
    return SheetsClient(tracker_ws=tracker, groups_ws=groups)


def get_filtered_group_links(client: SheetsClient, filter_tags: List[str]) -> List[str]:
    data = client.groups_ws.get_all_records()
    wanted = set(t.strip() for t in filter_tags)
    out: List[str] = []
    for row in data:
        tags = row.get("Tags", "")
        link = row.get("Group Link", "").strip()
        if not link:
            continue
        row_tags = set(t.strip() for t in tags.split(",") if t.strip())
        if wanted.issubset(row_tags):
            out.append(link)
    return out

