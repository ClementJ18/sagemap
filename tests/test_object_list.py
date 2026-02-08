"""Test ObjectsList asset parsing."""

from sagemap.assets import ObjectsList
from .conftest import create_context, load_asset_bytes


def test_objects_list():
    """Test ObjectsList asset parsing."""
    asset_bytes = load_asset_bytes("ObjectsList")
    
    context = create_context(asset_bytes)
    result = ObjectsList.parse(context)
    assert result is not None
