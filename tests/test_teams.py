"""Test Teams asset parsing."""

from sagemap.assets import Teams

from .conftest import create_context, load_asset_bytes


def test_teams():
    """Test Teams asset parsing."""
    asset_bytes = load_asset_bytes("Teams")

    context = create_context(asset_bytes)
    result = Teams.parse(context)
    assert result is not None
    assert hasattr(result, "teams")
    assert hasattr(result, "version")
