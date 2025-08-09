import pytest
from unittest.mock import Mock, call
from fb_groups_poster.sheets import get_filtered_group_links, SheetsClient

@pytest.fixture
def mock_sheets_client(mocker):
    """Fixture to create a mock SheetsClient."""
    mock_client = Mock(spec=SheetsClient)
    mock_client.groups_ws = mocker.Mock()
    mock_client.tracker_ws = mocker.Mock()
    return mock_client

def test_get_filtered_group_links(mock_sheets_client):
    # Given
    mock_data = [
        {"Group Link": "http://example.com/group1", "Tags": "rent, studio"},
        {"Group Link": "http://example.com/group2", "Tags": "rent"},
        {"Group Link": "http://example.com/group3", "Tags": "sale, apartment"},
        {"Group Link": "http://example.com/group4", "Tags": "rent, studio, pet-friendly"},
        {"Group Link": " ", "Tags": "rent, studio"}, # Empty link
        {"Group Link": "http://example.com/group6", "Tags": ""}, # Empty tags
    ]
    mock_sheets_client.groups_ws.get_all_records.return_value = mock_data

    # Test case 1: Filter by 'rent' and 'studio'
    # When
    result1 = get_filtered_group_links(mock_sheets_client, ["rent", "studio"])
    # Then
    assert result1 == ["http://example.com/group1", "http://example.com/group4"]

    # Test case 2: Filter by 'rent' only
    # When
    result2 = get_filtered_group_links(mock_sheets_client, ["rent"])
    # Then
    assert result2 == ["http://example.com/group1", "http://example.com/group2", "http://example.com/group4"]

    # Test case 3: Filter by a tag that doesn't exist
    # When
    result3 = get_filtered_group_links(mock_sheets_client, ["nonexistent"])
    # Then
    assert result3 == []

    # Test case 4: Filter with no tags
    # When
    result4 = get_filtered_group_links(mock_sheets_client, [])
    # Then
    assert result4 == [
        "http://example.com/group1",
        "http://example.com/group2",
        "http://example.com/group3",
        "http://example.com/group4",
        "http://example.com/group6",
    ]

def test_log_row(mocker):
    # Given
    # Patch datetime.now to have a predictable value
    mocker.patch('fb_groups_poster.sheets.datetime')
    from fb_groups_poster.sheets import datetime
    datetime.now.return_value.strftime.return_value = "MM/DD/YYYY HH:MM:SS"

    # Create a mock for the worksheet object
    mock_tracker_ws = Mock()

    # Instantiate the real SheetsClient with the mock worksheet
    client = SheetsClient(tracker_ws=mock_tracker_ws, groups_ws=Mock())

    # When
    client.log_row(
        content="Test Content",
        post_type="Test Type",
        details="Test Details",
        status="Test Status",
        notes="Test Notes",
        run_id="test-run-123"
    )

    # Then
    mock_tracker_ws.append_row.assert_called_once_with([
        "Test Content",
        "Test Type",
        "Test Details",
        "Test Status",
        "MM/DD/YYYY HH:MM:SS",
        "Test Notes",
        "test-run-123",
    ])
