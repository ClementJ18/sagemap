"""Test LibraryMapLists asset parsing."""

from sagemap.assets import LibraryMapLists
from .conftest import create_context, load_asset_bytes


def test_library_map_lists():
    """Test LibraryMapLists asset parsing."""
    asset_bytes = load_asset_bytes("LibraryMapLists")
    
    context = create_context(asset_bytes)
    result = LibraryMapLists.parse(context)
    assert result is not None
