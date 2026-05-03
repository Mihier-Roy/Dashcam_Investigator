// Connects to the Python Bridge over QWebChannel and exposes:
//   window.api       - the Bridge proxy
//   window.events    - EventTarget that re-broadcasts Qt signals
//   window.apiReady  - Promise<api>; resolves once the channel is wired
//
// Page scripts should always go through `apiReady` to avoid a race where
// they load after the channel handshake has already completed:
//
//     window.apiReady.then((api) => {
//         document.getElementById("btn-new").onclick = () => api.requestNewProject();
//         window.events.addEventListener("video", (e) => render(e.detail));
//     });

(function () {
    const shim = () => new Proxy({}, { get: () => () => undefined });

    window.events = new EventTarget();

    if (typeof QWebChannel === "undefined") {
        // Running outside Qt (e.g. opening a template directly in a browser
        // for design preview). Provide no-op shims so page scripts don't blow up.
        window.api = shim();
        window.apiReady = Promise.resolve(window.api);
        return;
    }

    window.apiReady = new Promise((resolve) => {
        new QWebChannel(qt.webChannelTransport, (channel) => {
            const bridge = channel.objects.bridge;
            window.api = bridge;

            const relay = (signalName, eventName, parse = true) => {
                if (!bridge[signalName]) return;
                bridge[signalName].connect((...args) => {
                    let payload = args.length === 1 ? args[0] : args;
                    if (parse && typeof payload === "string") {
                        try { payload = JSON.parse(payload); } catch (_) { /* keep raw */ }
                    }
                    window.events.dispatchEvent(new CustomEvent(eventName, { detail: payload }));
                });
            };

            relay("project_loaded",   "project");
            relay("video_changed",    "video");
            relay("notes_saved",      "notes-saved", false);
            relay("flag_changed",     "flag-changed", false);
            relay("theme_changed",    "theme", false);
            relay("progress",         "progress", false);
            relay("report_generated", "report", false);
            relay("focus_search",     "focus-search", false);
            relay("save_requested",   "save-requested", false);

            resolve(bridge);
        });
    });
})();
