"""Test PolygonTriggers asset parsing."""

import pytest
from map_parser.assets import PolygonTriggers
from .conftest import create_context, load_asset_bytes


@pytest.mark.skip(reason="No test data available for AssetList yet")
def test_polygon_triggers():
    """Test PolygonTriggers asset parsing."""
    asset_bytes = load_asset_bytes("PolygonTriggers")
    
    context = create_context(asset_bytes)
    result = PolygonTriggers.parse(context)
    assert result is not None
