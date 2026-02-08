"""Test GlobalVersion asset parsing."""

import pytest
from sagemap.assets import GlobalVersion
from .conftest import create_context, load_asset_bytes

    
@pytest.mark.skip(reason="No test data available for AssetList yet")
def test_global_version():
    """Test GlobalVersion asset parsing."""
    asset_bytes = load_asset_bytes("GlobalVersion")
    
    context = create_context(asset_bytes)
    result = GlobalVersion.parse(context)
    assert result is not None
    assert hasattr(result, 'version')
