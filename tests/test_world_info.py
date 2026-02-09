"""Test WorldInfo asset parsing."""

from sagemap.assets import WorldInfo

from .conftest import create_context, load_asset_bytes


def test_world_info():
    """Test WorldInfo asset parsing."""
    asset_bytes = load_asset_bytes("WorldInfo")

    context = create_context(asset_bytes)
    result = WorldInfo.parse(context)
    assert result is not None
