"""Tests for map_classes.py."""

from dashcam_investigator.core.map_classes import Mappy


class TestMappyTileLayers:
    """Regression coverage for Mappy.add_tilelayers()."""

    def test_add_tilelayers_does_not_raise(self):
        """All configured base tile layers must be valid folium/xyzservices
        provider names. Regression: "OpenStreet Map" (typo, missing space)
        and the discontinued "Stamen Terrain"/"Stamen Toner" providers were
        treated as custom tile URLs by folium, which raises ValueError for
        lacking an attribution -- breaking every map generation.
        """
        mappy = Mappy(average_point=(51.5074, -0.1278))
        mappy.add_tilelayers()

        tile_names = {
            child.tile_name
            for child in mappy.canvas._children.values()
            if hasattr(child, "tile_name")
        }
        assert "openstreetmap" in tile_names

    def test_add_tilelayers_avoids_key_gated_providers(self):
        """Regression: CartoDB Positron/Voyager return HTTP 200 but now
        serve a watermark tile reading "API key required" in production
        (verified by fetching real tiles), so no configured layer may
        point at a cartocdn.com tile URL.
        """
        mappy = Mappy(average_point=(51.5074, -0.1278))
        mappy.add_tilelayers()

        tile_urls = {
            child.tiles
            for child in mappy.canvas._children.values()
            if hasattr(child, "tiles")
        }
        assert not any("cartocdn.com" in url for url in tile_urls)
