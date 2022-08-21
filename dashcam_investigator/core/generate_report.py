import json
import logging
import pandas as pd
from pathlib import Path
from project_manager.project_datatypes import ProjectStructure

logger = logging.getLogger(__name__)


def generate_report(project_object: ProjectStructure):
    # Identify flagged videos
    logger.debug(f"Beginning report generation.")
    flagged_vids = [
        video for video in project_object.video_files if video.flagged == True
    ]
    case_name = project_object.project_info.case_name
    investigator_name = project_object.project_info.investigator_name
    output_file = Path(
        project_object.project_info.project_directory,
        "Reports",
        f"{case_name}_report.html",
    )

    logger.debug(f"Generating HTML report")
    list_of_links = ""
    notes_dict = dict()
    hash_dict = dict()
    info_dict = dict()
    for video in flagged_vids:
        dict_key = video.name[0:-4]
        list_of_links += f'<li><a href="{video.output_files[0]}" onclick="openFiles(\'{Path(video.output_files[1]).as_posix()}\')">{dict_key}</a></li>'
        notes_dict[dict_key] = video.notes
        hash_dict[dict_key] = video.sha256_hash
        video_meta = pd.read_csv(video.meta_files[1])
        info_dict[
            dict_key
        ] = f'Create Date : {video_meta["CreateDate"].values[0]} \r Video Duration: {video_meta["Duration"].values[0]} \r Device Information: {video_meta["Format"].values[0]} {video_meta["Information"].values[0]}'

    # Convert notes dict to JSON
    video_notes = json.dumps(notes_dict)
    video_hash = json.dumps(hash_dict)
    video_info = json.dumps(info_dict)

    # Create a HTML report with the relevant data
    html_report = f"""<html>
<head>
<title>Dashcam Investigator Case Report</title>
</head>
<style>
    /* Split the screen */
    .split {{
        height: 100%;
        position: fixed;
        z-index: 1;
        top: 0;
        overflow-x: hidden;
        padding-top: 20px;
    }}

    /* Control the left side */
    .left {{
        left: 0;
        width: 20%;
        color: white;
        background-color: #111;
    }}

    .left a {{
        color: white;
    }}

    /* Control the right side */
    .right {{
        width: 78%;
        right: 0;
    }}

    /* Center contnet */
    .centered {{
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        text-align: center;
    }}

    #noteContent {{
        border-left: 6px solid #ccc !important;
        color: #000 !important;
        background-color: #ddffff !important;
        border-color: #2196F3 !important;
        padding: 1em 16px;
        display: none;
    }}
</style>

<script>
    const notes = {video_notes}
    const hashes = {video_hash}
    const info = {video_info}
    function openFiles(speed_graph_url) {{
        event.preventDefault()
        document.getElementById("map-iframe").src = event.target.href;
        document.getElementById("graph-iframe").src = speed_graph_url;
        document.getElementById("videoTitle").innerText = "Selected video : " + event.target.innerText;
        document.getElementById("hashTitle").innerText = "SHA256 Hash : " + hashes[event.target.innerText];
        document.getElementById("infoTitle").innerText = info[event.target.innerText];
        document.getElementById("videoNotes").innerText = "Video Notes";
        document.getElementById("noteContent").innerText = notes[event.target.innerText];
        document.getElementById("noteContent").style.display = "block"
        document.getElementById("placeholder").style.display = "none"
    }}
</script>

<body>
    <div class="split left">
        <div class="centered">
            <h2>Dashcam Investigator Case Report</h2>
            <h3>Case Name : {case_name} </h3>
            <h3>Investigator Name : {investigator_name} </h3>
            <h4 style="float: left;">Flagged videos:</h4>
            <ul>
                {list_of_links}
            </ul>
        </div>
    </div>
    
    <div class="split right">
        <div id="notes">
            <h1 id="placeholder">Please select a video</h1>
            <h3 id="videoTitle"></h3>
            <h4 id="hashTitle"></h4>
            <h5 id="infoTitle"></h4>
            <h4 id="videoNotes"></h4>
            <p id="noteContent" />
        </div>
        <iframe id="map-iframe" height="60%" width="90%"></iframe>
        <iframe id="graph-iframe" height="60%" width="90%"></iframe>
    </div>

</body>
</html>
"""

    # Write report to output file
    logger.debug(f"Writing report to file -> {output_file}")
    with output_file.open("w") as file:
        file.write(html_report)
    logger.debug(f"Completed report generation.")

    return output_file
