"""Test NamedCameras asset parsing."""

from map_parser.assets import NamedCameras
from .conftest import create_context, load_asset_bytes


def test_named_cameras():
    """Test NamedCameras asset parsing."""
    asset_bytes = load_asset_bytes("NamedCameras")
    
    context = create_context(asset_bytes)
    result = NamedCameras.parse(context)
    assert result is not None
