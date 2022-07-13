import json
import logging
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
    for video in flagged_vids:
        list_of_links += f'<li><a href="{video.output_files[0]}" onclick="openMap()">{video.name[0:-4]}</a></li>'
        notes_dict[video.name[0:-4]] = video.notes

    # Convert notes dict to JSON
    video_notes = json.dumps(notes_dict)

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
    function openMap() {{
        event.preventDefault()
        document.getElementById("iframe").src = event.target.href;
        document.getElementById("videoTitle").innerText = "Selected video : " + event.target.innerText;
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
            <h4 id="videoNotes"></h4>
            <p id="noteContent" />
        </div>
        <iframe id="iframe" height="65%" width="95%"></iframe>
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
