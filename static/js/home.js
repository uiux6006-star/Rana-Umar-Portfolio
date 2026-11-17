/* ==========================================
        HOME PAGE: spotlight, 3D tilt, process line
========================================== */

(function () {

    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const finePointer = window.matchMedia("(pointer: fine)").matches;

    /* ---------- Spotlight that follows the mouse ---------- */

    if (finePointer) {
        document.querySelectorAll(".hp-spot").forEach((card) => {
            card.addEventListener("pointermove", (e) => {
                const r = card.getBoundingClientRect();
                card.style.setProperty("--mx", `${e.clientX - r.left}px`);
                card.style.setProperty("--my", `${e.clientY - r.top}px`);
            });
        });
    }

    /* ---------- 3D tilt on project images ---------- */

    if (finePointer && !reduceMotion) {
        document.querySelectorAll("[data-tilt]").forEach((el) => {
            el.addEventListener("pointermove", (e) => {
                const r = el.getBoundingClientRect();
                const x = (e.clientX - r.left) / r.width - 0.5;
                const y = (e.clientY - r.top) / r.height - 0.5;
                el.style.transform = `perspective(1000px) rotateY(${x * 8}deg) rotateX(${-y * 6}deg) translateY(-4px)`;
            });
            el.addEventListener("pointerleave", () => { el.style.transform = ""; });
        });
    }

    /* ---------- Process line fills as you scroll ---------- */

    const process = document.getElementById("hpProcess");

    if (process) {
        const steps = [...process.querySelectorAll("li")];
        const update = () => {
            const r = process.getBoundingClientRect();
            const start = window.innerHeight * 0.8;
            const progress = Math.min(1, Math.max(0, (start - r.top) / (r.height + window.innerHeight * 0.3)));
            const fill = reduceMotion ? 1 : progress;
            process.style.setProperty("--fill", fill.toFixed(3));
            steps.forEach((li, i) => li.classList.toggle("is-on", fill >= i / steps.length + 0.05 || fill === 1));
        };
        window.addEventListener("scroll", update, { passive: true });
        window.addEventListener("resize", update, { passive: true });
        update();
    }

})();
