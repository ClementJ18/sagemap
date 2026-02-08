"""Test StandingWaterAreas asset parsing."""

from sagemap.assets import StandingWaterAreas
from .conftest import create_context, load_asset_bytes


def test_standing_water_areas():
    """Test StandingWaterAreas asset parsing."""
    asset_bytes = load_asset_bytes("StandingWaterAreas")
    
    context = create_context(asset_bytes)
    result = StandingWaterAreas.parse(context)
    assert result is not None
