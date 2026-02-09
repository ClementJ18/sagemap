"""Test SidesList and BuildLists asset parsing."""

from sagemap.assets import SidesList

from .conftest import create_context, load_asset_bytes


def test_sides_list():
    """Test SidesList asset parsing."""
    asset_bytes = load_asset_bytes("SidesList")

    context = create_context(asset_bytes)
    result = SidesList.parse(context, False)
    assert result is not None
