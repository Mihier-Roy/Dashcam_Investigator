import logging

from branca.colormap import linear
from folium import FeatureGroup
from pandas import DataFrame

from dashcam_investigator.core.map_classes import (
    Mappy,
    RouteLineMaker,
    StartMarkerPopup,
)

logger = logging.getLogger(__name__)


def initialise_map(video_metadata: DataFrame) -> Mappy:
    """
    Initialises an instance of the Mappy class, which manages a folium map
    """
    logger.debug("Initialising map")
    mappy = Mappy(video_metadata)
    mappy.add_tilelayers()
    mappy.add_draw_options()
    mappy.generate_feature_groups()
    mappy.add_layer_control()
    mappy.add_measure_control()
    return mappy


def generate_speed_colour_map(speed: DataFrame) -> linear:
    """
    Takes in a dataframe containing a large list of speed, and uses this to generate a branca linear colour map.
    """
    colour_map = linear.Set1_09.scale(speed["Speed"].min(), speed["Speed"].max())
    colour_map.caption = "Speed colour scale: "
    return colour_map


def add_data_to_map(
    video,
    routelines: FeatureGroup,
    start_markers: FeatureGroup,
    speed_lines: FeatureGroup,
    routeline_colour: str,
    colour_map: linear,
):
    """
    Takes a MetaDataFrames instance, three folium FeatureGroups, and a
    linear branca colour map. Builds a RouteLineMaker for the video and
    uses it to add a routeline, start marker, and speed-coloured line to
    the map.
    """
    logger.debug("Adding routlines, start markers to the map")
    routeliner = RouteLineMaker(
        gps_df=video.gps_df,
        points=video.points,
        routeline_group=routelines,
        start_marker_group=start_markers,
        colour_line_group=speed_lines,
    )
    routeliner.make_routeline(routeline_colour)
    marker_popup = StartMarkerPopup(video.file_info_df).start_marker_popup_html()
    routeliner.make_start_marker(marker_popup)
    routeliner.make_routeline_with_speed_colouring(colour_map)
