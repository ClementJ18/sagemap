"""Test full map parsing for all maps in tests/data/maps/."""

from pathlib import Path

import pytest

from sagemap import parse_map_from_path


def get_test_maps():
    """Get all map files from tests/data/maps/ directory."""
    maps_dir = Path(__file__).parent / "data" / "maps"
    if not maps_dir.exists():
        return []
    return list(maps_dir.glob("*.map"))


@pytest.mark.parametrize("map_path", get_test_maps(), ids=lambda p: p.name)
def test_parse_map(map_path):
    """Test full parsing of individual map files.

    This test ensures that each map in the test data directory can be:
    1. Successfully parsed without errors
    2. Produces a valid Map object
    3. Can be converted to a dictionary (for serialization)
    """
    # Parse the map
    map_obj = parse_map_from_path(str(map_path))

    # Verify we got a valid map object
    assert map_obj is not None, f"Failed to parse map: {map_path.name}"

    # Verify the map can be converted to dict (tests serialization)
    map_dict = map_obj.to_dict()
    assert map_dict is not None, f"Failed to convert map to dict: {map_path.name}"
    assert isinstance(map_dict, dict), f"to_dict() did not return a dict: {map_path.name}"


def test_maps_directory_exists():
    """Verify that the maps test data directory exists."""
    maps_dir = Path(__file__).parent / "data" / "maps"
    assert maps_dir.exists(), "tests/data/maps/ directory does not exist"


def test_has_test_maps():
    """Verify that there are map files to test."""
    maps = get_test_maps()
    assert len(maps) > 0, "No .map files found in tests/data/maps/ directory"
