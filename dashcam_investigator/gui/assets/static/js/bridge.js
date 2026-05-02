// Connects to the Python Bridge over QWebChannel and exposes a single
// `window.api` plus an EventTarget that re-broadcasts Qt signals.
//
// Usage from page scripts:
//     window.addEventListener("api:ready", () => {
//         window.api.selectVideo("foo.mp4");
//     });
//     window.events.addEventListener("video", (e) => { ... });

(function () {
    if (typeof QWebChannel === "undefined") {
        // Running outside Qt (e.g. opening a template directly in a browser
        // for design preview). Provide a no-op shim so page scripts don't blow up.
        window.api = new Proxy({}, { get: () => () => undefined });
        window.events = new EventTarget();
        return;
    }

    window.events = new EventTarget();

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

        window.dispatchEvent(new Event("api:ready"));
    });
})();
