/* ==========================================
        PROJECTS PAGE: category filter + search
   (spotlight on cards comes from home.js)
========================================== */

(function () {

    const grid = document.getElementById("pjGrid");
    if (!grid) return;

    const cards = [...grid.querySelectorAll(".pj-card")];
    const buttons = [...document.querySelectorAll(".pj-filter")];
    const search = document.getElementById("pjSearch");
    const count = document.getElementById("pjCount");
    const empty = document.getElementById("pjEmpty");
    const reset = document.getElementById("pjReset");
    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    let filter = "all";
    let timer = null;

    const matches = (card, query) =>
        (filter === "all" || card.dataset.category === filter) &&
        (!query || query.split(/\s+/).every((word) => card.dataset.search.includes(word)));

    const apply = () => {
        const query = search ? search.value.trim().toLowerCase() : "";
        const show = cards.filter((card) => matches(card, query));
        const hide = cards.filter((card) => !show.includes(card));

        if (count) count.textContent = show.length;
        if (empty) empty.hidden = show.length > 0;

        clearTimeout(timer);

        // Fade out the cards that no longer match, then remove them from the grid
        hide.forEach((card) => card.classList.add("is-leaving"));

        timer = setTimeout(() => {
            hide.forEach((card) => card.classList.add("is-hidden"));
            show.forEach((card) => {
                card.classList.remove("is-hidden");
                // Cards that move up may not have been scrolled into view yet
                card.classList.add("aos-animate");
            });
            requestAnimationFrame(() => show.forEach((card) => card.classList.remove("is-leaving")));
            if (window.AOS) window.AOS.refresh();
        }, reduceMotion ? 0 : 220);
    };

    const setFilter = (value) => {
        filter = buttons.some((b) => b.dataset.filter === value) ? value : "all";
        buttons.forEach((b) => {
            const on = b.dataset.filter === filter;
            b.classList.toggle("is-active", on);
            b.setAttribute("aria-pressed", on);
        });

        // Keep the filter in the URL so it can be shared (?category=django)
        const url = new URL(window.location);
        if (filter === "all") url.searchParams.delete("category");
        else url.searchParams.set("category", filter);
        history.replaceState(null, "", url);

        apply();
    };

    buttons.forEach((b) => b.addEventListener("click", () => setFilter(b.dataset.filter)));

    if (search) {
        search.addEventListener("input", apply);

        // Press "/" anywhere to jump to search, Escape to clear it
        document.addEventListener("keydown", (e) => {
            const typing = /^(INPUT|TEXTAREA|SELECT)$/.test(document.activeElement.tagName);
            if (e.key === "/" && !typing) {
                e.preventDefault();
                search.focus();
            }
        });
        search.addEventListener("keydown", (e) => {
            if (e.key === "Escape") {
                search.value = "";
                apply();
            }
        });
    }

    if (reset) {
        reset.addEventListener("click", () => {
            if (search) search.value = "";
            setFilter("all");
        });
    }

    // Start from ?category=... if the link had one
    const initial = new URLSearchParams(window.location.search).get("category");
    if (initial) setFilter(initial);

})();
