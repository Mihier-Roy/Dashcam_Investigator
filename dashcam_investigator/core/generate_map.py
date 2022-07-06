from pathlib import Path
from core.generate_dataframe import MetaDataFrames, make_speed_dataframe
from core.map_functions import (
    add_data_to_map,
    generate_speed_colour_map,
    initialise_map,
)
from project_manager.project_datatypes import FileAttributes


def generate_map(video_file: FileAttributes, output_dir: Path):
    # Convert extracted metadata to Dataframe
    video_meta_handler = MetaDataFrames(video_file.name, video_file.meta_files)
    video_meta_handler.convert_to_datetime()
    video_meta_handler.add_speed()
    video_meta_handler.add_label_for_speed_chart()

    speed_data = make_speed_dataframe(video_meta_handler)

    # Compute mean and median GPS coordinates
    mean_point = (
        video_meta_handler.gps_df["Latitude"].mean(),
        video_meta_handler.gps_df["Longitude"].mean(),
    )
    median_point = (
        video_meta_handler.gps_df["Latitude"].mean(),
        video_meta_handler.gps_df["Longitude"].mean(),
    )

    mappy = initialise_map(mean_point)
    colour_map = generate_speed_colour_map(speed_data)
    mappy.canvas.add_child(colour_map)
    add_data_to_map(
        video_meta_handler,
        mappy.routelines,
        mappy.start_markers,
        mappy.speed_lines,
        "blue",
        colour_map,
    )
    mappy.canvas.save(output_dir)
