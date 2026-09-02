// Notes panel: edit notes for the currently selected video, plus
// flag/un-flag. Auto-saves on blur if text changed; toast confirms
// every save / flag round-trip via Bridge signals.

const state = {
    current: null,        // currently displayed video (FileAttributes shape)
    lastSavedText: "",    // baseline used for blur-driven dirty check
};

function showToast(text, kind = "success", timeoutMs = 1600) {
    const el = $("notes-toast");
    el.className = `toast toast-${kind}`;
    el.textContent = text;
    el.hidden = false;
    el.dataset.timer && clearTimeout(Number(el.dataset.timer));
    if (timeoutMs > 0) {
        const t = setTimeout(() => { el.hidden = true; }, timeoutMs);
        el.dataset.timer = String(t);
    }
}

function updateFlagLabel(flagged) {
    $("btn-flag-label").textContent = flagged ? "Un-flag video" : "Flag video";
    $("btn-flag").setAttribute("aria-pressed", flagged ? "true" : "false");
}

function applyVideo(v) {
    const text = $("notes-text");
    const btnSave = $("btn-save");
    const btnFlag = $("btn-flag");
    const title = $("notes-title");
    const subtitle = $("notes-subtitle");

    if (!v || !v.name) {
        state.current = null;
        state.lastSavedText = "";
        text.value = "";
        text.disabled = true;
        btnSave.disabled = true;
        btnFlag.disabled = true;
        title.textContent = "No video selected";
        subtitle.textContent = "Select a video from the sidebar to add notes.";
        $("notes-toast").hidden = true;
        return;
    }

    state.current = v;
    state.lastSavedText = v.notes || "";
    text.value = state.lastSavedText;
    text.disabled = false;
    btnSave.disabled = false;
    btnFlag.disabled = false;
    title.textContent = v.name;
    title.title = v.name;
    subtitle.textContent = v.flagged ? "Flagged for review" : "";
    updateFlagLabel(v.flagged);
    $("notes-toast").hidden = true;
}

window.apiReady.then((api) => {
    const text = $("notes-text");
    const btnSave = $("btn-save");
    const btnFlag = $("btn-flag");

    window.events.addEventListener("video", (e) => applyVideo(e.detail));

    window.events.addEventListener("notes-saved", (e) => {
        if (e.detail !== state.current?.name) return;
        state.lastSavedText = text.value;
        showToast("Notes saved", "success");
    });

    window.events.addEventListener("flag-changed", (e) => {
        const [name, flagged] = e.detail;
        if (name !== state.current?.name) return;
        state.current.flagged = flagged;
        updateFlagLabel(flagged);
        $("notes-subtitle").textContent = flagged ? "Flagged for review" : "";
        showToast(flagged ? "Video flagged" : "Video un-flagged", "flag");
    });

    btnSave.addEventListener("click", () => {
        if (!state.current) return;
        api.saveNotes(state.current.name, text.value);
    });

    btnFlag.addEventListener("click", () => {
        if (!state.current) return;
        api.setFlag(state.current.name, !state.current.flagged);
    });

    text.addEventListener("blur", () => {
        if (!state.current) return;
        if (text.value !== state.lastSavedText) {
            api.saveNotes(state.current.name, text.value);
        }
    });

    // Ctrl+S anywhere in the app routes here via the bridge.
    window.events.addEventListener("save-requested", () => {
        if (!state.current) return;
        if (text.value !== state.lastSavedText) {
            api.saveNotes(state.current.name, text.value);
        } else {
            showToast("Already saved", "success");
        }
    });
});
