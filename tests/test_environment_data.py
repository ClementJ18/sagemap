"""Test EnvironmentData asset parsing."""

from sagemap.assets import EnvironmentData

from .conftest import create_context, load_asset_bytes


def test_environment_data():
    """Test EnvironmentData asset parsing."""
    asset_bytes = load_asset_bytes("EnvironmentData")

    context = create_context(asset_bytes)
    result = EnvironmentData.parse(context)
    assert result is not None
