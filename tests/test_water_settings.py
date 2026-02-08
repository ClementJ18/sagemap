"""Test WaterSettings asset parsing."""
import pytest 

from sagemap.assets import WaterSettings
from .conftest import create_context, load_asset_bytes


@pytest.mark.skip(reason="No test data available for AssetList yet")
def test_water_settings():
    """Test WaterSettings asset parsing."""
    asset_bytes = load_asset_bytes("WaterSettings")
    
    context = create_context(asset_bytes)
    result = WaterSettings.parse(context)
    assert result is not None
