"""Test AssetList asset parsing."""

import pytest

from sagemap.assets import AssetList

from .conftest import create_context, load_asset_bytes


@pytest.mark.skip(reason="No test data available for AssetList yet")
def test_asset_list():
    """Test AssetList asset parsing."""
    asset_bytes = load_asset_bytes("AssetList")

    context = create_context(asset_bytes)
    result = AssetList.parse(context)
    assert result is not None
