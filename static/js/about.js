/* ==========================================
        ABOUT PAGE: counters, timeline fill, local clock
   (spotlight + 3D tilt come from home.js)
========================================== */

(function () {

    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    /* ---------- Count-up stats ---------- */

    const format = (el, n) => {
        const pad = Number(el.dataset.pad || 0);
        return String(n).padStart(pad, "0") + (el.dataset.suffix || "");
    };

    const countUp = (el) => {
        const target = Number(el.dataset.count);
        if (!target || reduceMotion) return;
        const duration = 1400;
        const start = performance.now();
        const tick = (now) => {
            const t = Math.min(1, (now - start) / duration);
            const eased = 1 - Math.pow(1 - t, 3);
            el.textContent = format(el, Math.round(target * eased));
            if (t < 1) requestAnimationFrame(tick);
        };
        requestAnimationFrame(tick);
    };

    const counters = document.querySelectorAll("[data-count]");

    if ("IntersectionObserver" in window) {
        const io = new IntersectionObserver((entries) => {
            entries.forEach((entry) => {
                if (!entry.isIntersecting) return;
                countUp(entry.target);
                io.unobserve(entry.target);
            });
        }, { threshold: 0.6 });
        counters.forEach((el) => io.observe(el));
    }

    /* ---------- Timeline line fills as you scroll ---------- */

    const timeline = document.getElementById("abTimeline");

    if (timeline) {
        const items = [...timeline.querySelectorAll("li")];
        let queued = false;

        const update = () => {
            queued = false;
            const r = timeline.getBoundingClientRect();
            const mark = window.innerHeight * 0.6;
            const progress = Math.min(1, Math.max(0, (mark - r.top) / r.height));
            const fill = reduceMotion ? 1 : progress;
            timeline.style.setProperty("--fill", fill.toFixed(3));
            items.forEach((li) => {
                const node = li.querySelector(".ab-node");
                const nodeTop = node.getBoundingClientRect().top;
                li.classList.toggle("is-on", reduceMotion || nodeTop < mark);
            });
        };

        const queue = () => {
            if (!queued) {
                queued = true;
                requestAnimationFrame(update);
            }
        };

        window.addEventListener("scroll", queue, { passive: true });
        window.addEventListener("resize", queue, { passive: true });
        update();
    }

    /* ---------- Local time in Pakistan ---------- */

    const clock = document.getElementById("abClock");

    if (clock) {
        const fmt = new Intl.DateTimeFormat("en-GB", {
            hour: "2-digit",
            minute: "2-digit",
            timeZone: "Asia/Karachi"
        });
        const tick = () => { clock.textContent = fmt.format(new Date()); };
        tick();
        setInterval(tick, 30000);
    }

})();
