# Google Sheets Integration Setup Guide

## Prerequisites

1. Install required packages:

```bash
pip install gspread google-auth
```

## Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Sheets API and Google Drive API

## Step 2: Create a Service Account

1. In Google Cloud Console, go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "Service Account"
3. Fill in the service account details
4. Click "Create and Continue"
5. Skip the optional steps and click "Done"

## Step 3: Generate Service Account Key

1. Click on your newly created service account
2. Go to the "Keys" tab
3. Click "Add Key" > "Create new key"
4. Choose "JSON" format
5. Download the JSON file and rename it to `service-account-key.json`
6. Place it in the same directory as your `auto_post_facebook.py` script

## Step 4: Share Your Google Sheet

1. Open your Google Sheet (the one shown in the image)
2. Click the "Share" button
3. Add your service account email (found in the JSON file) with "Editor" permissions
4. Copy the Spreadsheet ID from the URL:
   - URL format: `https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit`
   - Copy the SPREADSHEET_ID part

## Step 5: Update Configuration

In `auto_post_facebook.py`, update these variables:

```python
SERVICE_ACCOUNT_FILE = 'service-account-key.json'  # Your downloaded JSON file
SPREADSHEET_ID = 'your-spreadsheet-id'  # The ID you copied from the URL
WORKSHEET_NAME = 'Content_tracker'  # The name of your worksheet
```

## What Gets Logged

The script will automatically log:

- **Content**: First 50 characters of your post text
- **Type**: "Group post"
- **Details**: Group URL or error message
- **Status**: "Posted" or "Error"
- **Post date**: Current date
- **Notes**: Number of images or error details

## Security Notes

- Keep your `service-account-key.json` file secure and never commit it to version control
- Add `service-account-key.json` to your `.gitignore` file
- The service account has limited permissions to only access the specific spreadsheet you share
