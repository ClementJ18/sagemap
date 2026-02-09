"""Test MPPositionsList asset parsing."""

from sagemap.assets import MPPositionsList

from .conftest import create_context, load_asset_bytes


def test_mp_positions_list():
    """Test MPPositionsList asset parsing."""
    asset_bytes = load_asset_bytes("MPPositionList")

    context = create_context(asset_bytes)
    result = MPPositionsList.parse(context)
    assert result is not None
