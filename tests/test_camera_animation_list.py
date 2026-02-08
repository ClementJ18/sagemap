"""Test CameraAnimationList asset parsing."""

from sagemap.assets import CameraAnimationList
from .conftest import create_context, load_asset_bytes


def test_camera_animation_list():
    """Test CameraAnimationList asset parsing."""
    asset_bytes = load_asset_bytes("CameraAnimationList")
    
    context = create_context(asset_bytes)
    result = CameraAnimationList.parse(context)
    assert result is not None
