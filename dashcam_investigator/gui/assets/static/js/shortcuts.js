// Global keyboard shortcuts shared by every WebPanel.
// All shortcuts go through the Bridge so they work regardless of which
// panel currently has focus.
//
//   /          focus the sidebar filter (skipped when typing)
//   f          toggle flag on the currently selected video
//   ←/→        previous / next video (↑/↓ row navigation lives in sidebar.js)
//   Ctrl+S     save the notes panel's current text
//   ?          show the keyboard shortcuts overlay

(function () {
    function isTyping(target) {
        if (!target) return false;
        const tag = target.tagName;
        if (tag === "INPUT" || tag === "TEXTAREA") return true;
        return target.isContentEditable === true;
    }

    function call(method) {
        if (!window.apiReady) return;
        window.apiReady.then((api) => {
            if (api && typeof api[method] === "function") {
                try { api[method](); } catch (_) { /* ignore */ }
            }
        });
    }

    document.addEventListener("keydown", (event) => {
        // Always swallow Ctrl+S so the browser save-page dialog never appears
        // inside the app. Bridge fans the request out to whichever panel has
        // unsaved state (today: notes).
        if ((event.ctrlKey || event.metaKey) && (event.key === "s" || event.key === "S")) {
            event.preventDefault();
            call("requestSaveNotes");
            return;
        }

        // Single-key shortcuts: skip while the user is typing.
        if (isTyping(event.target)) return;
        if (event.altKey || event.ctrlKey || event.metaKey) return;

        switch (event.key) {
            case "/":
                event.preventDefault();
                call("focusSearch");
                break;
            case "f":
            case "F":
                event.preventDefault();
                call("toggleFlagCurrent");
                break;
            case "ArrowRight":
                event.preventDefault();
                call("selectNextVideo");
                break;
            case "ArrowLeft":
                event.preventDefault();
                call("selectPreviousVideo");
                break;
            case "?":
                event.preventDefault();
                call("requestShortcutsHelp");
                break;
            default:
                break;
        }
    });
})();
