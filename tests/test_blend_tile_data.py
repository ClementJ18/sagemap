"""Test BlendTileData asset parsing."""

from sagemap.assets import BlendTileData, HeightMapData
from .conftest import create_context, load_asset_bytes


def test_blend_tile_data():
    """Test BlendTileData asset parsing."""
    asset_bytes = load_asset_bytes("BlendTileData")
    heght_map_bytes = load_asset_bytes("HeightMapData")
    
    context = create_context(asset_bytes)
    height_map_context = create_context(heght_map_bytes)

    height_map = HeightMapData.parse(height_map_context)
    result = BlendTileData.parse(context, height_map)
    assert result is not None
