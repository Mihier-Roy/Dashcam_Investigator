import logging
from pathlib import Path

import gpxpy
from pandas import DataFrame, read_csv, to_datetime

from dashcam_investigator.exceptions import GPSParseError

logger = logging.getLogger(__name__)


class MetaDataFrames:
    """
    Manages GPS, temporal, and file information for a video file.
    Takes in a dict of metadata output files with keys "gpx" and "csv".
    """

    def __init__(self, video_name: str, video_meta_files: dict):
        self.video_name = video_name
        self.file_info_df = read_csv(video_meta_files["csv"])
        self.gps_df, self.points = self.process_gpx_to_df(Path(video_meta_files["gpx"]))

    def process_gpx_to_df(self, file_name: Path):
        """
        Read the GPX file created and convert it into a dataframe.
        Also extract the route travelled in the video.
        Raises GPSParseError if the file has no tracks or segments.
        """
        logger.debug(f"Creating dataframe from GPX file -> {file_name}")
        with file_name.open() as gpxfile:
            gpx = gpxpy.parse(gpxfile)

        if not gpx.tracks or not gpx.tracks[0].segments:
            raise GPSParseError(f"GPX file has no tracks or segments: {file_name.name}")

        track = gpx.tracks[0]
        segment = track.segments[0]
        data = []
        for point_idx, point in enumerate(segment.points):
            # get_speed returns m/s; convert to km/h
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

        points = []
        for segment in track.segments:
            for point in segment.points:
                points.append((point.latitude, point.longitude))

        logger.debug(
            f"Generated dataframe and points list for route lines -> {file_name}"
        )
        return gpx_df, points

    def convert_to_datetime(self):
        """
        Converts the date and time columns in the dataframe to datetime objects.
        GPS datetimes from gpxpy are already Python datetime objects; CreateDate
        strings from exiftool use ISO format (%Y-%m-%d %H:%M:%S).
        """
        logger.debug("Converting time formats to pandas datetime objects")
        self.gps_df["DateTime"] = to_datetime(
            arg=self.gps_df["DateTime"], utc=True, errors="coerce"
        )
        self.file_info_df["CreateDate"] = to_datetime(
            arg=self.file_info_df["CreateDate"],
            format="%Y-%m-%d %H:%M:%S",
            errors="coerce",
        )

    def add_label_for_speed_chart(self):
        """
        Adds a column to the dataframe to identify the source of the data.
        """
        logger.debug("Adding datasource field to dataframe")
        self.gps_df["DataSource"] = len(self.gps_df.index) * [
            "Extracted metadata using exiftool"
        ]

    def add_speed(self):
        """
        Calculates the average speed for the video and adds it to the file info dataframe.
        """
        logger.debug("Adding average and max speed to file info dataframe")
        self.file_info_df["AverageSpeed"] = round(self.gps_df["Speed"].mean(), 2)
        self.file_info_df["MaxSpeed"] = round(self.gps_df["Speed"].max(), 2)


def make_speed_dataframe(video_meta_handler) -> DataFrame:
    """
    Takes in a MetaDataFrames handler and returns a dataframe with speed and datetime.
    """
    logger.debug("Generating speed dataframe for speed graph")
    speed_data = video_meta_handler.gps_df[["Speed", "DateTime", "DataSource"]]
    return speed_data
