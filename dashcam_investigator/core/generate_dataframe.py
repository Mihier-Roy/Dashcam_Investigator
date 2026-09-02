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
        points_list = segment.points

        # Dashcam/GPMF GPX tracks stamp a timestamp on only a fraction of
        # points (e.g. once per second at 18Hz sampling), so gpxpy's
        # per-point get_speed() -- which needs both neighbours timed --
        # returns None almost everywhere. Compute speed once per interval
        # between consecutive *timed* points and apply it to every point
        # in that interval instead.
        speeds: list[float | None] = [None] * len(points_list)
        timed_indices = [i for i, p in enumerate(points_list) if p.time is not None]
        for start_idx, end_idx in zip(timed_indices, timed_indices[1:]):
            start_point, end_point = points_list[start_idx], points_list[end_idx]
            elapsed_seconds = (end_point.time - start_point.time).total_seconds()
            distance_metres = start_point.distance_3d(end_point)
            if distance_metres is None:
                distance_metres = start_point.distance_2d(end_point)
            if elapsed_seconds <= 0 or distance_metres is None:
                continue
            speed_kmh = (distance_metres / elapsed_seconds) * 3.6
            for i in range(start_idx, end_idx):
                speeds[i] = speed_kmh

        data = [
            [point.longitude, point.latitude, point.elevation, point.time, speed]
            for point, speed in zip(points_list, speeds)
        ]
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
        """
        logger.debug("Converting time formats to pandas datetime objects")
        try:
            self.gps_df["DateTime"] = to_datetime(
                arg=self.gps_df["DateTime"], format="%d-%m-%Y %H:%M:%S"
            )
        except Exception:
            self.gps_df["DateTime"] = to_datetime(
                arg=self.gps_df["DateTime"], format="%y:%m:%d %H:%M:%S"
            )

        self.file_info_df["CreateDate"] = to_datetime(
            arg=self.file_info_df["CreateDate"], format="%d-%m-%Y %H:%M:%S"
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
