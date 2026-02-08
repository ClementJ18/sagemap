"""Test HeightMapData asset parsing."""

from map_parser.assets import HeightMapData
from .conftest import create_context, load_asset_bytes


def test_height_map_data():
    """Test HeightMapData asset parsing."""
    asset_bytes = load_asset_bytes("HeightMapData")
    
    context = create_context(asset_bytes)
    result = HeightMapData.parse(context)
    assert result is not None
