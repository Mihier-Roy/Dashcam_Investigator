window.apiReady.then((api) => {
    const newBtn = document.getElementById("btn-new");
    const openBtn = document.getElementById("btn-open");
    if (newBtn) newBtn.addEventListener("click", () => api.requestNewProject());
    if (openBtn) openBtn.addEventListener("click", () => api.requestOpenProject());
});
