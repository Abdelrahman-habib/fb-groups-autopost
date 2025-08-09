import pytest
from click.testing import CliRunner
from fb_groups_poster.cli import main
from fb_groups_poster.config import AppConfig, SheetsConfig, BrowserConfig, PosterConfig

@pytest.fixture
def mock_config():
    """Fixture for a dummy AppConfig."""
    return AppConfig(
        sheets=SheetsConfig(service_account_file="dummy.json", spreadsheet_id="dummy_id"),
        browser=BrowserConfig(edge_profile_dir="dummy_dir"),
        poster=PosterConfig(text="dummy text", image_paths=[], filter_tags=[])
    )

def test_run_success(mocker, mock_config):
    """Test the CLI run command succeeds."""
    # Given
    runner = CliRunner()
    mocker.patch('fb_groups_poster.cli.os.path.exists', return_value=True)
    mocker.patch('fb_groups_poster.cli.load_config', return_value=mock_config)
    mock_run_posting = mocker.patch('fb_groups_poster.cli.run_posting', return_value=True)

    # When
    result = runner.invoke(main, ['run', '--config', 'dummy.yaml'])

    # Then
    assert result.exit_code == 0
    mock_run_posting.assert_called_once_with(mock_config, assume_yes=False)

def test_run_config_not_found(mocker):
    """Test the CLI run command fails if config not found."""
    # Given
    runner = CliRunner()
    mocker.patch('fb_groups_poster.cli.os.path.exists', return_value=False)

    # When
    result = runner.invoke(main, ['run', '--config', 'nonexistent.yaml'])

    # Then
    assert result.exit_code == 1
    assert "Config file not found" in result.output

def test_run_verbose_logging(mocker, mock_config):
    """Test that -v flag sets logging to DEBUG."""
    # Given
    runner = CliRunner()
    mocker.patch('fb_groups_poster.cli.os.path.exists', return_value=True)
    mocker.patch('fb_groups_poster.cli.load_config', return_value=mock_config)
    mocker.patch('fb_groups_poster.cli.run_posting', return_value=True)
    mock_logging = mocker.patch('fb_groups_poster.cli.logging')

    # When
    result = runner.invoke(main, ['run', '-v'])

    # Then
    assert result.exit_code == 0
    mock_logging.basicConfig.assert_called_once()
    # Check that the log level was set to DEBUG
    assert mock_logging.basicConfig.call_args[1]['level'] == mock_logging.DEBUG

def test_run_default_logging(mocker, mock_config):
    """Test that logging is INFO by default."""
    # Given
    runner = CliRunner()
    mocker.patch('fb_groups_poster.cli.os.path.exists', return_value=True)
    mocker.patch('fb_groups_poster.cli.load_config', return_value=mock_config)
    mocker.patch('fb_groups_poster.cli.run_posting', return_value=True)
    mock_logging = mocker.patch('fb_groups_poster.cli.logging')

    # When
    result = runner.invoke(main, ['run'])

    # Then
    assert result.exit_code == 0
    mock_logging.basicConfig.assert_called_once()
    # Check that the log level was set to INFO
    assert mock_logging.basicConfig.call_args[1]['level'] == mock_logging.INFO
