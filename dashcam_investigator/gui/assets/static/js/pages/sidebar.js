// Sidebar: list / tree of project videos with search, selection,
// and flag badges. Driven entirely by Bridge.project_loaded /
// flag_changed / video_changed signals.

const SVG_VIDEO  = '<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><polygon points="23 7 16 12 23 17 23 7"/><rect x="1" y="5" width="15" height="14" rx="2" ry="2"/></svg>';
const SVG_FOLDER = '<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>';
const SVG_CHEVRON = '<svg class="icon chevron" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"/></svg>';

const state = {
    project: null,
    filterText: "",
    mode: "list",
    selected: null,
    collapsedFolders: new Set(),
};

const body = $("sidebar-body");
const filterInput = $("filter");
const caseName = $("case-name");
const caseMeta = $("case-meta");

function filterVideos(videos) {
    const q = state.filterText.toLowerCase().trim();
    if (!q) return videos;
    return videos.filter((v) =>
        (v.name || "").toLowerCase().includes(q) ||
        (v.sha256_hash || "").toLowerCase().includes(q)
    );
}

function videoRowHtml(video) {
    const sel = state.selected === video.name ? " selected" : "";
    const flag = video.flagged ? '<span class="badge badge-flag">Flagged</span>' : "";
    const hash = video.sha256_hash
        ? `<div class="meta mono truncate" title="${escapeHtml(video.sha256_hash)}">${escapeHtml(video.sha256_hash.slice(0, 16))}…</div>`
        : "";
    return `
        <div class="list-row${sel}" data-name="${escapeHtml(video.name)}">
            ${SVG_VIDEO}
            <div class="fill">
                <div class="title truncate" title="${escapeHtml(video.name)}">${escapeHtml(video.name)}</div>
                ${hash}
            </div>
            ${flag}
        </div>
    `;
}

function renderEmpty(title, body_text) {
    body.innerHTML = `
        <div class="empty">
            ${SVG_VIDEO}
            <div class="empty-title">${escapeHtml(title)}</div>
            <div>${escapeHtml(body_text)}</div>
        </div>
    `;
}

function renderList() {
    if (!state.project) return renderEmpty("No project loaded", "Open or create a project to populate the sidebar.");
    const videos = filterVideos(state.project.video_files || []);
    if (videos.length === 0) {
        return renderEmpty("No matches", state.filterText ? "Try a different filter." : "This project has no videos.");
    }
    body.innerHTML = `<div class="list">${videos.map(videoRowHtml).join("")}</div>`;
}

// Tree mode ------------------------------------------------------------
function normPath(p) { return String(p || "").replace(/\\/g, "/"); }

function buildTree(videos, rootPath) {
    const root = { folders: {}, files: [] };
    const rootNorm = normPath(rootPath).replace(/\/+$/, "");
    for (const v of videos) {
        let p = normPath(v.file_path);
        if (rootNorm && p.startsWith(rootNorm + "/")) {
            p = p.slice(rootNorm.length + 1);
        }
        const parts = p.split("/").filter(Boolean);
        parts.pop();  // drop the file name; the video itself sits in `files`
        let node = root;
        for (const part of parts) {
            node.folders[part] = node.folders[part] || { folders: {}, files: [] };
            node = node.folders[part];
        }
        node.files.push(v);
    }
    return root;
}

function renderTreeNode(node, path) {
    const folderEntries = Object.entries(node.folders).sort(([a], [b]) => a.localeCompare(b));
    const fileEntries = [...node.files].sort((a, b) => a.name.localeCompare(b.name));
    let html = "";

    for (const [folderName, child] of folderEntries) {
        const childPath = path ? `${path}/${folderName}` : folderName;
        const isCollapsed = state.collapsedFolders.has(childPath);
        html += `
            <div class="tree-folder${isCollapsed ? " collapsed" : ""}" data-folder="${escapeHtml(childPath)}">
                ${SVG_CHEVRON}
                ${SVG_FOLDER}
                <span>${escapeHtml(folderName)}</span>
            </div>
            <div class="tree-children${isCollapsed ? " collapsed" : ""}" data-folder-children="${escapeHtml(childPath)}">
                ${renderTreeNode(child, childPath)}
            </div>
        `;
    }
    for (const v of fileEntries) {
        html += videoRowHtml(v);
    }
    return html;
}

function renderTree() {
    if (!state.project) return renderEmpty("No project loaded", "Open or create a project to populate the sidebar.");
    const rootPath = state.project.project_info?.input_directory || "";
    const videos = filterVideos(state.project.video_files || []);
    if (videos.length === 0) {
        return renderEmpty("No matches", state.filterText ? "Try a different filter." : "This project has no videos.");
    }
    const tree = buildTree(videos, rootPath);
    body.innerHTML = `<div class="list tree">${renderTreeNode(tree, "")}</div>`;
}

function render() {
    if (state.mode === "list") renderList();
    else renderTree();
}

function updateHeader() {
    if (!state.project || !state.project.project_info) {
        caseName.textContent = "No project loaded";
        caseMeta.textContent = "Open or create a project to begin.";
        return;
    }
    const info = state.project.project_info;
    const count = (state.project.video_files || []).length;
    caseName.textContent = info.case_name || "Untitled case";
    caseName.title = info.case_name || "";
    caseMeta.textContent = `${count} video${count === 1 ? "" : "s"} · ${info.investigator_name || "—"}`;
}

window.apiReady.then((api) => {
    const applyProject = (project) => {
        state.project = project;
        state.collapsedFolders.clear();
        updateHeader();
        render();
    };

    window.events.addEventListener("project", (e) => applyProject(e.detail));

    // The bridge's project_loaded signal fires once and isn't replayed, so
    // a panel whose QWebChannel handshake finishes after that emission
    // (e.g. a project opened at startup, before this page is fully wired
    // up) would otherwise show "No project loaded" forever. Pull the
    // current state once as well as listening for future pushes.
    api.getProjectJson((json) => {
        try {
            const project = JSON.parse(json);
            if (project) applyProject(project);
        } catch (_) {
            /* no project yet */
        }
    });

    window.events.addEventListener("flag-changed", (e) => {
        const [name, flagged] = e.detail;
        const video = (state.project?.video_files || []).find((v) => v.name === name);
        if (video) {
            video.flagged = flagged;
            render();
        }
    });

    window.events.addEventListener("video", (e) => {
        const v = e.detail;
        if (v && v.name) {
            state.selected = v.name;
            render();
        }
    });

    window.events.addEventListener("focus-search", () => {
        filterInput.focus();
        filterInput.select();
    });

    body.addEventListener("click", (e) => {
        const folder = e.target.closest(".tree-folder");
        if (folder) {
            const key = folder.dataset.folder;
            if (state.collapsedFolders.has(key)) state.collapsedFolders.delete(key);
            else state.collapsedFolders.add(key);
            render();
            return;
        }
        const row = e.target.closest(".list-row");
        if (row) {
            const name = row.dataset.name;
            state.selected = name;
            api.selectVideo(name);
            render();
        }
    });

    filterInput.addEventListener("input", (e) => {
        state.filterText = e.target.value;
        render();
    });

    document.querySelectorAll(".sidebar-tabs .tab").forEach((tab) => {
        tab.addEventListener("click", () => {
            state.mode = tab.dataset.mode;
            document.querySelectorAll(".sidebar-tabs .tab").forEach((t) => {
                const active = t === tab;
                t.classList.toggle("active", active);
                t.setAttribute("aria-selected", active ? "true" : "false");
            });
            render();
        });
    });
});
