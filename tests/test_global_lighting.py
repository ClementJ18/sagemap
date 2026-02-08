"""Test GlobalLighting asset parsing."""

from sagemap.assets import GlobalLighting
from .conftest import create_context, load_asset_bytes


def test_global_lighting():
    """Test GlobalLighting asset parsing."""
    asset_bytes = load_asset_bytes("GlobalLighting")
    
    context = create_context(asset_bytes)
    result = GlobalLighting.parse(context)
    assert result is not None
