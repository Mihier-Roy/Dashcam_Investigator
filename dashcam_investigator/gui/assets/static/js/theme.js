// Receives theme changes from Qt and applies them to <html>. Phase 2 will
// hook this up to a Qt-side QStyleHints listener; for now it just reacts
// to whatever the bridge emits.

(function () {
    const apply = (name) => {
        if (name === "system") {
            document.documentElement.removeAttribute("data-theme");
        } else if (name === "light" || name === "dark") {
            document.documentElement.setAttribute("data-theme", name);
        }
    };

    window.addEventListener("api:ready", () => {
        window.events.addEventListener("theme", (e) => apply(e.detail));
    });
})();
