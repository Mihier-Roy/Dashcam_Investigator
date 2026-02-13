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


def add_routeline_to_map(
    gps_df: DataFrame,
    points,
    routeline_group: FeatureGroup,
    start_marker_group: FeatureGroup,
    colour_line_group: FeatureGroup,
) -> RouteLineMaker:
    """
    Takes in a dataframe containing GPS and temporal data, as well as featuregroups for a routeline, start marker, and speed line.
    Uses this data to generate an instance of the RouteLineMaker class, and returns the instance
    """
    routeliner = RouteLineMaker(
        gps_df, points, routeline_group, start_marker_group, colour_line_group
    )
    return routeliner


def add_start_marker_to_map(file_info_df: DataFrame, routeliner: RouteLineMaker):
    """
    Takes in a dataframe containing file information for a video and an instance of the RouteLineMaker class associated with that file.
    Uses the file information dataframe to make a popup for a start marker. Calls the make_start_marker() method for the RouteLineMaker instance to add
    the popup to a start marker
    """
    marker_popup = StartMarkerPopup(file_info_df).start_marker_popup_html()
    routeliner.make_start_marker(marker_popup)


def add_speedline_to_map(routeliner: RouteLineMaker, colour_map: linear):
    """
    Takes in an instance of the RouteLineMaker class and a linear branca colormap.
    Calls a method for the RouteLineMaker instance which uses the colour map to add a speed line to the map.
    """
    routeliner.make_routeline_with_speed_colouring(colour_map)


def add_data_to_map(
    video,
    routelines: FeatureGroup,
    start_markers: FeatureGroup,
    speed_lines: FeatureGroup,
    routeline_colour: str,
    colour_map: linear,
):
    """
    Takes in either a list of Video (video.py) or MetaDataFrames (dataframer.py) instances, three folium FeatureGroups, and a linear branca colour map.
    Makes a RouteLineMaker (mapper_classes.py) instance for each video in the video list, and uses these instances to add routelines, start markers, and speed lines to a folium Map
    """
    logger.debug("Adding routlines, start markers to the map")
    # for video in video_list:
    routeliner = add_routeline_to_map(
        gps_df=video.gps_df,
        points=video.points,
        routeline_group=routelines,
        start_marker_group=start_markers,
        colour_line_group=speed_lines,
    )
    routeliner.make_routeline(routeline_colour)
    add_start_marker_to_map(video.file_info_df, routeliner)
    add_speedline_to_map(routeliner, colour_map)
