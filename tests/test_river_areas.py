"""Test RiverAreas asset parsing."""

from sagemap.assets import RiverAreas

from .conftest import create_context, load_asset_bytes


def test_river_areas():
    """Test RiverAreas asset parsing."""
    asset_bytes = load_asset_bytes("RiverAreas")

    context = create_context(asset_bytes)
    result = RiverAreas.parse(context)
    assert result is not None
