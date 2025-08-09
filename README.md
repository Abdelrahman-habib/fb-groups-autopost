## fb-groups-poster

> Status: Proof of Concept (POC). This tool is for experimentation/demos, not production use. Expect breaking changes and FB UI fragility.

Automate posting to Facebook Groups using your Microsoft Edge profile, with Google Sheets for group selection and run tracking. Provides a clean CLI with stage spinners, a progress bar (tqdm) with ETA, and optional verbose logs.

### Features

- Use your real Edge profile to post (no storing FB credentials in code)
- Headless or visible browser runs
- Google Sheets driven:
  - Worksheet `Groups` with columns `Group Link` and `Tags`
  - Worksheet `auto-poster-tracker` to track run events and per-group results
- Filter target groups by tags (must match all tags)
- Pretty CLI:
  - Stage spinners with checkmarks for key steps
  - tqdm progress bar with ETA, last-iteration time, success/error counts
  - Optional verbose logs (`-v`) for debugging

### Requirements

- Python 3.10+
- Microsoft Edge installed (althoug you can easily edit the code to use chrome or any other browser)
- An Edge profile that is logged in to the Facebook account used for posting
- A Google Cloud Service Account JSON key with access to your Google Sheet

### Install

Using Poetry (recommended):

```bash
poetry install
# run the CLI via Poetry
poetry run fbpost run
```

Using pip/virtualenv:

```bash
python -m venv .venv
source .venv/Scripts/activate  # Windows Git Bash / PowerShell: .venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install .
# run the CLI directly
fbpost run
```

### Quick start

1. Copy and edit `config.example.yaml` → `config.yaml`:

```yaml
sheets:
  service_account_file: ./service-account-key.json
  spreadsheet_id: your-spreadsheet-id
  tracker_sheet: auto-poster-tracker (or any other sheet name you want)
  groups_sheet: Groups (or any other sheet name you want)

browser:
  edge_profile_dir: "C:/Users/YourName/AppData/Local/Microsoft/Edge/User Data"
  edge_profile_name: "Default" # or "Profile 1", etc.
  headless: true # set to false to watch the browser

poster:
  text: |
    Your post text here...
  image_paths:
    - F:/path/to/image1.jpg
    - F:/path/to/image2.jpg
  filter_tags:
    - rent
    - studio
```

2. Prepare your Google Sheet:

- Share it with the service account email (Editor)
- `Groups` worksheet with columns:
  - `Group Link` (Facebook group URL)
  - `Tags` (comma-separated, e.g. `rent, studio`)
- `auto-poster-tracker` worksheet to receive logs (optional header row):
  - `Content, Type, Details, Status, Post date, Notes, Run ID`

Example Google Sheet (layout reference): [auto-poster-tracker-example](https://docs.google.com/spreadsheets/d/1DYLijtg_jSyutX9quIus1zLVdC8z6pfoRoqeziLEktI/edit?usp=sharing)

3. Run it:

```bash
fbpost run
```

### CLI usage

```bash
fbpost run [--config PATH] [-y|--yes] [-v]
```

- `--config PATH` (default `config.yaml`): path to YAML config
- `-y, --yes`: skip confirmation prompts
- `-v`: verbose (debug) logging; without `-v` Selenium/WebDriver logs are suppressed

Examples:

```bash
fbpost run -y                    # no prompts
fbpost run -v                    # verbose logs
fbpost run --config my.cfg.yaml  # custom config path
```

### What the app does

1. Initialize Google Sheets client (using your service account file)
2. Fetch and filter group links by `poster.filter_tags`
3. Confirm the number of groups (skip with `-y`)
4. Launch Edge with your profile (headless if enabled)
5. For each group:
   - Open group URL
   - Create a post, paste or type your text
   - Upload image(s)
   - Click Post and wait until Facebook finishes
   - Log the result to the tracker sheet
6. Quit browser and log a completion summary

### Configuration reference

- `sheets.service_account_file`: path to your JSON key (relative paths are normalized)
- `sheets.spreadsheet_id`: from the Sheet URL (`https://docs.google.com/spreadsheets/d/<ID>/edit`)
- `sheets.tracker_sheet`: tracker tab name (default `auto-poster-tracker`)
- `sheets.groups_sheet`: groups tab name (default `Groups`)
- `browser.edge_profile_dir`: the base Edge user data dir (ends with `.../Edge/User Data`)
- `browser.edge_profile_name`: e.g. `Default`, `Profile 1`, ...
- `browser.headless`: run Edge headlessly when `true`
- `poster.text`: the text content of your post
- `poster.image_paths`: list of image file paths (absolute recommended)
- `poster.filter_tags`: list of tags; only rows whose `Tags` include all of these will be targeted

Notes:

- Find your Edge profile path in `edge://version` → "Profile path"; split into:
  - `edge_profile_dir`: up to `User Data`
  - `edge_profile_name`: the last folder name (e.g., `Default`, `Profile 1`)
- Facebook UI should be English for the built-in selectors to work as-is.

### Logs and UI

- Pretty CLI:
  - Stage spinners with checkmarks for init/fetch/launch
  - `tqdm` progress bar for group posting with ETA and per-iteration stats
- Verbose logging (`-v`) prints debug details from the app
- Without `-v`, Selenium, urllib3, and webdriver-manager logs are suppressed
- Tracker logging to Sheets:
  - App start/finish events
  - Per-group success/error entries with notes and a run ID

### Troubleshooting

- "DevTools listening..." messages appear
  - They are suppressed by default; if you still see them, ensure you aren’t using `-v`. Some environments print once at startup—this is harmless.
- It can’t find the Edge profile or logs you out
  - Double-check `edge_profile_dir` and `edge_profile_name`; confirm in `edge://version`
- It fails to click or find elements
  - Ensure the FB UI language is English; DOM may differ by locale
  - Network/UI delays: increase waits or try non-headless mode to observe
- Images don’t upload
  - Use absolute Windows-style paths (e.g., `C:/path/file.jpg`)
- Google Sheets errors (permissions/worksheet)
  - Share the Sheet with the service account email printed inside the JSON
  - Confirm `tracker_sheet` and `groups_sheet` names match exactly
- Progress bar formatting looks off
  - Most terminals are supported; try a standard terminal or reduce width

### Development

- Code lives under `src/fb_groups_poster/`
- Main entry point: `fb_groups_poster/cli.py` (`fbpost` console script)
- Orchestrator: `fb_groups_poster/runner.py`
- Browser setup: `fb_groups_poster/browser.py`
- Sheets integration: `fb_groups_poster/sheets.py`
- Posting logic: `fb_groups_poster/poster.py`
- CLI UI helpers (spinner): `fb_groups_poster/cli_ui.py`

Run from source with Poetry:

```bash
poetry run fbpost run -y -v
```

### Google Sheets setup

See `google_sheets_setup.md` for a step-by-step guide to create a service account, share your Sheet, and find the Spreadsheet ID.

### License

MIT
