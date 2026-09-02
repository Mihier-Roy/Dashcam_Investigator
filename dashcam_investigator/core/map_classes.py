import logging

from branca import colormap
from folium import (
    ColorLine,
    FeatureGroup,
    Icon,
    IFrame,
    LayerControl,
    Map,
    Marker,
    Popup,
    TileLayer,
)
from folium.plugins import Draw, MeasureControl
from folium.vector_layers import PolyLine
from pandas import DataFrame

logger = logging.getLogger(__name__)


class RouteLineMaker:
    """
    Takes in a dataframe containing coordinates and speeds from a single dashcam video.
    Plots a single-coloured routeline on a folium map using those coordinates.
    Plots a routeline which is coloured based on the speed of the vehicle.
    Adds a marker to the start of the routeline with a popup containing information about the video file that is being plotted.
    """

    def __init__(
        self,
        gps_df: DataFrame,
        points,
        routeline_group: FeatureGroup,
        start_marker_group: FeatureGroup,
        colour_line_group: FeatureGroup,
    ):

        self.points = points
        self.speed = gps_df["Speed"].to_list()
        self.routeline_group = routeline_group
        self.start_marker_group = start_marker_group
        self.colour_line_group = colour_line_group

    def make_routeline(self, routeline_colour: str):
        """
        Take in a routeline colour (either blue for extracted metadata or purple for watermark data),
        and plot the coordinates stored by the class instance on the map
        """
        PolyLine(locations=self.points, color=routeline_colour).add_to(
            self.routeline_group
        )

    def make_routeline_with_speed_colouring(self, colour_map=colormap.linear):
        """
        Take in a branca linear color map, and use this to plot an additional routeline which uses the speeds stored by the class instance
        as a colour scale
        """
        ColorLine(
            positions=self.points, colors=self.speed, colormap=colour_map, weight=4.5
        ).add_to(self.colour_line_group)

    def make_start_marker(self, popup: Popup):
        """
        Take in a popup for a start marker, which contains an HTML table of file details, and add it to a start marker for the routelines.
        """
        Marker(
            location=self.points[0],
            tooltip="Start of route line. Click to see file details.",
            popup=popup,
            icon=Icon(icon="plus-circle", prefix="fa"),
        ).add_to(self.start_marker_group)


class StartMarkerPopup:
    """
    Parses the file information dataframe for a single video file into its separate components
    Generates the popup used by the RouteLineMaker class for its start marker using the parsed file information.
    """

    def __init__(self, file_info_df):
        self.file_name = str(file_info_df["SourceFile"].iloc[0])
        self.file_type = str(file_info_df["FileType"].iloc[0])
        self.file_size = str(file_info_df["FileSize"].iloc[0])
        self.MIMEType = str(file_info_df["MIMEType"].iloc[0])
        self.duration = str(file_info_df["Duration"].iloc[0])
        self.average_speed = str(file_info_df["AverageSpeed"].iloc[0])
        self.max_speed = str(file_info_df["MaxSpeed"].iloc[0])
        self.file_create_date = str(file_info_df["CreateDate"].iloc[0])

    def start_marker_popup_html(self) -> Popup:
        # Defines the HTML file details table
        self.popup_html = f"""<html lang="en">
        <head>
        <meta charset="UTF-8">
        <style>
        table {{
            font-family: arial, sans-serif;
            border-collapse: collapse;
            width: 100%;
        }}
        td, th {{
            border: 1px solid #dddddd;
            text-align: left;
            padding: 8px;
        }}
        tr:nth-child(even) {{
            background-color: #dddddd;
        }}
        </style>
        </head>
        <body>
        <h1>File Information</h1>
        <table style="width:100%">
            <tr><th>File Attribute(s)</th><th>Value(s)</th></tr>
            <tr><td>Name:</td><td>{self.file_name}</td></tr>
            <tr><td>File Type</td><td>{self.file_type}</td></tr>
            <tr><td>File Size</td><td>{self.file_size}</td></tr>
            <tr><td>MIME Type</td><td>{self.MIMEType}</td></tr>
            <tr><td>Video Length</td><td>{self.duration}</td></tr>
            <tr><td>Average Speed:</td><td>{self.average_speed}</td></tr>
            <tr><td>Highest Speed:</td><td>{self.max_speed}</td></tr>
            <tr><td>File Create Date and Time:</td><td>{self.file_create_date}</td></tr>
        </table>
        </body>
        </html>
        """
        iframe = IFrame(html=self.popup_html, width=500, height=300)
        popup = Popup(iframe, max_width=2650)

        return popup


class Mappy:
    """Class which stores the folium map canvas, adds tilelayers, adds draw options, and adds featuregroups"""

    def __init__(self, average_point):
        self.canvas = Map(location=average_point, zoom_start=12)

    def add_tilelayers(self):
        # Adds different map styles which can be freely switched between by
        # the user. CartoDB Positron/Voyager now require a Carto API key
        # in production (they still return HTTP 200, but the tile image
        # itself is a watermark reading "API key required") -- verified by
        # fetching sample tiles directly. Esri and OpenStreetMap.HOT are
        # confirmed key-less alternatives (xyzservices requires_token=False
        # plus a manual fetch check of real tile bytes).
        TileLayer("OpenStreetMap").add_to(self.canvas)
        TileLayer("OpenStreetMap.HOT").add_to(self.canvas)
        TileLayer("Esri.WorldTopoMap").add_to(self.canvas)

    def add_draw_options(self):
        # Adds draw options for the user
        Draw(
            export=True,
            filename="my_data.geojson",
            position="topleft",
            draw_options={"polyline": {"allowIntersection": False}},
            edit_options={"poly": {"allowIntersection": False}},
        ).add_to(self.canvas)

    def generate_feature_groups(self):
        """
        Makes the required feature groups. These groups represent display layers, and will contain features displayed on the map.
        Each feature group can be toggled on and off by the user from the interactive map file, with elements toggled on displayed on the map, and those toggled off removed.
        """
        self.routelines = FeatureGroup(name="Route line", show=True).add_to(self.canvas)
        self.speed_lines = FeatureGroup(
            name="Route line coloured by speed", show=False
        ).add_to(self.canvas)
        self.start_markers = FeatureGroup(
            name="Start markers for each video", show=True
        ).add_to(self.canvas)

    def add_layer_control(self):
        # adds the ability to hide and show featuregroups/tilelayers
        LayerControl().add_to(self.canvas)

    def add_measure_control(self):
        # adds the ability to measure the distance between two points
        MeasureControl(position="bottomleft").add_to(self.canvas)
