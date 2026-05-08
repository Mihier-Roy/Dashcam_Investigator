"""Tests for map_classes and map_functions."""


def test_mappy_has_no_add_tilelayers_method():
    """add_tilelayers was removed because Stamen tilesets were dropped in folium ≥ 0.14."""
    from dashcam_investigator.core.map_classes import Mappy

    assert not hasattr(Mappy, "add_tilelayers")


def test_tilelayer_not_imported_in_map_classes():
    """TileLayer import should be gone since it is no longer used."""
    import dashcam_investigator.core.map_classes as mc

    assert not hasattr(mc, "TileLayer")


def test_initialise_map_renders():
    """initialise_map must succeed without referencing Stamen tilesets."""
    from dashcam_investigator.core.map_functions import initialise_map

    mappy = initialise_map((37.77, -122.42))
    assert mappy is not None
    assert mappy.canvas is not None
