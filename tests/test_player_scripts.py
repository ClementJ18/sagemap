"""Test PlayerScriptsList asset parsing."""

from sagemap.assets import PlayerScriptsList

from .conftest import create_context, load_asset_bytes


def test_player_scripts_list():
    """Test PlayerScriptsList asset parsing."""
    asset_bytes = load_asset_bytes("PlayerScriptsList")

    context = create_context(asset_bytes)
    result = PlayerScriptsList.parse(context)
    assert result is not None
