"""Test StandingWaveAreas asset parsing."""

from sagemap.assets import StandingWaveAreas

from .conftest import create_context, load_asset_bytes


def test_standing_wave_areas():
    """Test StandingWaveAreas asset parsing."""
    asset_bytes = load_asset_bytes("StandingWaveAreas")

    context = create_context(asset_bytes)
    result = StandingWaveAreas.parse(context)
    assert result is not None
