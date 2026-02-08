"""Test PostEffectsChunk asset parsing."""

from sagemap.assets import PostEffectsChunk
from .conftest import create_context, load_asset_bytes


def test_post_effects_chunk():
    """Test PostEffectsChunk asset parsing."""
    asset_bytes = load_asset_bytes("PostEffectsChunk")
    
    context = create_context(asset_bytes)
    result = PostEffectsChunk.parse(context)
    assert result is not None
