import logging
import gpxpy
from pathlib import Path
from pandas import read_csv, to_datetime, DataFrame

logger = logging.getLogger(__name__)


class MetaDataFrames:
    """
    Manages GPS, temporal, and file information for a video file
    Takes in a list of metadata output files containing one of each of the following file types:
    - A GPS data file
    - A temporal data file
    - A file containing information about the original video file
    Also takes in a list of ExclusionZone objects, and a temp directory for output files
    """

    def __init__(self, video_name: str, video_meta_files: list):
        self.video_name = video_name
        self.file_info_df = read_csv(f"{video_meta_files[1]}")
        self.gps_df, self.points = self.process_gpx_to_df(Path(video_meta_files[0]))

    def process_gpx_to_df(self, file_name: Path):
        """
        Read the GPX file created and convert it into a dataframe.
        Also extract the route travelled in the video.
        """
        logger.debug(f"Creating dataframe from GPX file -> {file_name}")
        with file_name.open() as gpxfile:
            gpx = gpxpy.parse(gpxfile)

        # Create a DataFrame
        track = gpx.tracks[0]
        segment = track.segments[0]
        # Load the data into a Pandas dataframe (by way of a list)
        data = []
        for point_idx, point in enumerate(segment.points):
            # get_speed returns m/s. Convert to km/h
            speed = (
                segment.get_speed(point_idx) * 3.6
                if segment.get_speed(point_idx) is not None
                else None
            )
            data.append(
                [point.longitude, point.latitude, point.elevation, point.time, speed]
            )
        columns = [
            "Longitude",
            "Latitude",
            "Altitude",
            "DateTime",
            "Speed",
        ]
        gpx_df = DataFrame(data, columns=columns)

        # Create points tuple for lines
        points = []
        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    points.append(tuple([point.latitude, point.longitude]))

        logger.debug(
            f"Generated dataframe and points list for route lines -> {file_name}"
        )
        return gpx_df, points

    def convert_to_datetime(self):
        """
        Converts the date and time columns in the dataframe to datetime objects, allowing them to be used for other functions
        """
        logger.debug(f"Converting time formats to pandas datetime objects")
        try:
            self.gps_df["DateTime"] = to_datetime(
                arg=self.gps_df["DateTime"], format="%d-%m-%Y %H:%M:%S"
            )
        except:
            self.gps_df["DateTime"] = to_datetime(
                arg=self.gps_df["DateTime"], format="%y:%m:%d %H:%M:%S"
            )

        self.file_info_df["CreateDate"] = to_datetime(
            arg=self.file_info_df["CreateDate"], format="%d-%m-%Y %H:%M:%S"
        )

    def add_label_for_speed_chart(self):
        """
        Adds a column to the dataframe to identify the source of the data. This is done to make a legend for the speed chart.
        """
        logger.debug(f"Adding datasource field to dataframe")
        self.gps_df["DataSource"] = len(self.gps_df.index) * [
            "Extracted metadata using exiftool"
        ]

    def add_speed(self):
        """
        Calculates the average speed for the video and adds it to the file info dataframe
        """
        logger.debug(f"Adding average and max speed to file info dataframe")
        self.file_info_df["AverageSpeed"] = round(self.gps_df["Speed"].mean(), 2)
        self.file_info_df["MaxSpeed"] = round(self.gps_df["Speed"].max(), 2)


def make_speed_dataframe(video_meta_handler) -> DataFrame:
    """
    Takes in a list of video data handlers - either ocr or metadata
    returns a dataframe containing the speeds and datetimes in the list
    """
    logger.debug("Generating speed dataframe for speed graph")
    speed_data = video_meta_handler.gps_df[["Speed", "DateTime", "DataSource"]]
    return speed_data


def find_final_point_in_route(video_list: list) -> tuple:
    """Takes in a list of video data handlers - either ocr or metadata, and returns the final available coordinate"""
    final_point = video_list[-1].gps_df["Latitude, Longitude"].iloc[-1]
    return final_point
