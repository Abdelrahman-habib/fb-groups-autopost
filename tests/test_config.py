import os
import yaml
import pytest
from fb_groups_poster.config import load_config, AppConfig, SheetsConfig, BrowserConfig, PosterConfig

@pytest.fixture
def temp_config_file(tmp_path):
    config_data = {
        "sheets": {
            "service_account_file": "fake_service_account.json",
            "spreadsheet_id": "fake_spreadsheet_id",
        },
        "browser": {
            "edge_profile_dir": "/fake/edge/profile/dir",
            "edge_profile_name": "TestProfile",
            "headless": True,
        },
        "poster": {
            "text": "Hello, world!",
            "image_paths": ["/fake/path/image1.jpg", "image2.jpg"],
            "filter_tags": ["test", "demo"],
        },
    }
    config_path = tmp_path / "config.yaml"
    with open(config_path, "w") as f:
        yaml.dump(config_data, f)

    # Create a dummy service account file to test absolute path conversion
    (tmp_path / "fake_service_account.json").touch()

    # Change directory to tmp_path to test relative path conversion
    os.chdir(tmp_path)

    return config_path

def test_load_config(temp_config_file):
    # When
    config = load_config(str(temp_config_file))

    # Then
    assert isinstance(config, AppConfig)

    # Check SheetsConfig
    assert isinstance(config.sheets, SheetsConfig)
    assert config.sheets.spreadsheet_id == "fake_spreadsheet_id"
    assert config.sheets.service_account_file == os.path.abspath("fake_service_account.json")

    # Check BrowserConfig
    assert isinstance(config.browser, BrowserConfig)
    assert config.browser.edge_profile_dir == "/fake/edge/profile/dir"
    assert config.browser.edge_profile_name == "TestProfile"
    assert config.browser.headless is True

    # Check PosterConfig
    assert isinstance(config.poster, PosterConfig)
    assert config.poster.text == "Hello, world!"
    assert config.poster.image_paths == [os.path.abspath("/fake/path/image1.jpg"), os.path.abspath("image2.jpg")]
    assert config.poster.filter_tags == ["test", "demo"]
