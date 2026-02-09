"""Test WaypointsList asset parsing."""

from sagemap.assets import WaypointsList

from .conftest import create_context, load_asset_bytes


def test_waypoints_list():
    """Test WaypointsList asset parsing."""
    asset_bytes = load_asset_bytes("WaypointsList")

    context = create_context(asset_bytes)
    result = WaypointsList.parse(context)
    assert result is not None
