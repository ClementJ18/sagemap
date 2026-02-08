"""Test TriggerAreas asset parsing."""

from map_parser.assets import TriggerAreas
from .conftest import create_context, load_asset_bytes


def test_trigger_areas():
    """Test TriggerAreas asset parsing."""
    asset_bytes = load_asset_bytes("TriggerAreas")
    
    context = create_context(asset_bytes)
    result = TriggerAreas.parse(context)
    assert result is not None
