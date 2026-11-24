/* ==========================================
        CASE STUDY: screenshot / live / mobile preview
   The iframe only loads when someone asks for the live preview.
========================================== */

(function () {

    "use strict";

    const box = document.getElementById("csPreview");
    if (!box) return;

    const buttons = [...box.querySelectorAll("[data-mode]")];
    const shot = box.querySelector(".cs-shot");
    const wrap = box.querySelector(".cs-frame-wrap");
    const frame = wrap && wrap.querySelector("iframe");

    buttons.forEach((b) => b.addEventListener("click", () => {
        const mode = b.dataset.mode;
        buttons.forEach((x) => {
            x.classList.toggle("is-active", x === b);
            x.setAttribute("aria-pressed", x === b);
        });

        if (mode === "shot" || !frame) {
            shot.hidden = false;
            if (wrap) wrap.hidden = true;
            box.classList.remove("is-live", "is-mobile");
            return;
        }

        if (!frame.src) frame.src = frame.dataset.src;
        shot.hidden = true;
        wrap.hidden = false;
        box.classList.add("is-live");
        box.classList.toggle("is-mobile", mode === "mobile");
    }));

})();
