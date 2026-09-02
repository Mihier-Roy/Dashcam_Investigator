// Metadata panel: sortable, filterable property/value table for the
// currently selected video. Data arrives via api.getMetadataJson(name).

const state = {
    rows: [],
    filter: "",
    sortKey: "property",
    sortDir: "asc",
    currentName: null,
};

const tbody = $("metadata-tbody");
const filterInput = $("filter");

function applyFilterAndSort() {
    const q = state.filter.trim().toLowerCase();
    let items = state.rows;
    if (q) {
        items = items.filter((r) =>
            String(r.property ?? "").toLowerCase().includes(q) ||
            String(r.value ?? "").toLowerCase().includes(q)
        );
    }
    items = [...items].sort((a, b) => {
        const av = String(a[state.sortKey] ?? "").toLowerCase();
        const bv = String(b[state.sortKey] ?? "").toLowerCase();
        return state.sortDir === "asc" ? av.localeCompare(bv) : bv.localeCompare(av);
    });
    return items;
}

function render() {
    const items = applyFilterAndSort();

    if (items.length === 0) {
        tbody.innerHTML = `<tr><td colspan="2" class="metadata-empty">${state.rows.length === 0
            ? "Select a video to view metadata."
            : "No matches."}</td></tr>`;
    } else {
        tbody.innerHTML = items.map((r) => `
            <tr>
                <td>${escapeHtml(r.property)}</td>
                <td class="value mono" title="Click to copy">${escapeHtml(r.value)}</td>
            </tr>
        `).join("");
    }

    document.querySelectorAll("th.sortable").forEach((th) => {
        const isSorted = th.dataset.sort === state.sortKey;
        th.classList.toggle("sorted", isSorted);
        const indicator = th.querySelector(".sort-indicator");
        if (indicator) indicator.textContent = isSorted ? (state.sortDir === "asc" ? "↑" : "↓") : "↕";
        th.setAttribute("aria-sort", isSorted
            ? (state.sortDir === "asc" ? "ascending" : "descending")
            : "none");
    });
}

function loadMetadata(api, name) {
    state.currentName = name;
    if (!name) {
        state.rows = [];
        render();
        return;
    }
    api.getMetadataJson(name, (json) => {
        try { state.rows = JSON.parse(json) || []; }
        catch (_) { state.rows = []; }
        render();
    });
}

window.apiReady.then((api) => {
    window.events.addEventListener("video", (e) => {
        const v = e.detail;
        loadMetadata(api, v?.name || null);
    });

    filterInput.addEventListener("input", (e) => {
        state.filter = e.target.value;
        render();
    });

    const onSort = (th) => {
        const key = th.dataset.sort;
        if (state.sortKey === key) {
            state.sortDir = state.sortDir === "asc" ? "desc" : "asc";
        } else {
            state.sortKey = key;
            state.sortDir = "asc";
        }
        render();
    };
    document.querySelectorAll("th.sortable").forEach((th) => {
        th.addEventListener("click", () => onSort(th));
        th.addEventListener("keydown", (e) => {
            if (e.key === "Enter" || e.key === " ") {
                e.preventDefault();
                onSort(th);
            }
        });
    });

    tbody.addEventListener("click", (e) => {
        const td = e.target.closest("td.value");
        if (!td) return;
        const original = td.textContent;
        const writeText = navigator.clipboard?.writeText.bind(navigator.clipboard);
        Promise.resolve(writeText ? writeText(original) : null)
            .then(() => {
                td.textContent = "Copied!";
                setTimeout(() => { td.textContent = original; }, 800);
            })
            .catch(() => { /* ignore — clipboard may be blocked */ });
    });
});
