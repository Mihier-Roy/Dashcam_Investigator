// Applies whatever theme the Qt-side ThemeManager emits.

(function () {
    const apply = (name) => {
        if (name === "system") {
            document.documentElement.removeAttribute("data-theme");
        } else if (name === "light" || name === "dark") {
            document.documentElement.setAttribute("data-theme", name);
        }
    };

    window.apiReady.then(() => {
        window.events.addEventListener("theme", (e) => apply(e.detail));
    });
})();
