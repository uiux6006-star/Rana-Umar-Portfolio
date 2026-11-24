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

    /* ---------- Skills Universe ---------- */

    const universe = document.getElementById("skillsUniverse");
    const dataTag = document.getElementById("suData");

    if (universe && dataTag) {
        const skills = JSON.parse(dataTag.textContent);
        const byId = Object.fromEntries(skills.map((s) => [s.id, s]));
        const map = document.getElementById("suMap");
        const svg = map.querySelector(".su-lines");
        const panel = document.getElementById("suPanel");
        const nodes = [...map.querySelectorAll(".su-node")];
        const nodeById = Object.fromEntries(nodes.map((n) => [n.dataset.id, n]));
        const groupLabels = Object.fromEntries(
            [...universe.querySelectorAll(".su-filter[data-group]")].map((b) => [b.dataset.group, b.textContent.trim()])
        );
        let selected = null;

        // Two rings: core skills inside, concepts and tools outside
        const inner = skills.filter((s) => s.group === "frontend" || s.group === "backend");
        const outer = skills.filter((s) => s.group === "concepts" || s.group === "design");
        const place = (list, rx, ry, offset) => list.forEach((s, i) => {
            const a = offset + (i / list.length) * Math.PI * 2;
            nodeById[s.id].style.setProperty("--x", (50 + Math.cos(a) * rx).toFixed(2) + "%");
            nodeById[s.id].style.setProperty("--y", (50 + Math.sin(a) * ry).toFixed(2) + "%");
        });
        place(inner, 23, 25, -Math.PI / 2);
        place(outer, 42, 43, -Math.PI / 2 + Math.PI / outer.length);

        // Connections (each pair once)
        const edges = [];
        const seen = new Set();
        skills.forEach((s) => s.related.forEach((r) => {
            const key = [s.id, r].sort().join("|");
            if (byId[r] && !seen.has(key)) { seen.add(key); edges.push([s.id, r]); }
        }));

        const NS = "http://www.w3.org/2000/svg";
        function drawLines() {
            if (getComputedStyle(svg).display === "none") return;
            const box = map.getBoundingClientRect();
            svg.setAttribute("viewBox", `0 0 ${box.width} ${box.height}`);
            svg.textContent = "";
            const center = (id) => {
                const icon = nodeById[id].querySelector("i").getBoundingClientRect();
                return [icon.left + icon.width / 2 - box.left, icon.top + icon.height / 2 - box.top];
            };
            edges.forEach(([a, b]) => {
                const [x1, y1] = center(a);
                const [x2, y2] = center(b);
                const path = document.createElementNS(NS, "path");
                const mx = (x1 + x2) / 2 + (box.width / 2 - (x1 + x2) / 2) * .25;
                const my = (y1 + y2) / 2 + (box.height / 2 - (y1 + y2) / 2) * .25;
                path.setAttribute("d", `M${x1},${y1} Q${mx},${my} ${x2},${y2}`);
                path.dataset.a = a;
                path.dataset.b = b;
                if (selected && (a === selected || b === selected)) path.classList.add("is-on");
                svg.appendChild(path);
            });
        }

        const el = (tag, cls, text) => {
            const n = document.createElement(tag);
            if (cls) n.className = cls;
            if (text != null) n.textContent = text;
            return n;
        };

        function showPanel(s) {
            panel.textContent = "";
            const card = el("div", "su-detail");

            const head = el("div", "su-detail-head");
            const icon = el("span", "su-detail-icon");
            icon.appendChild(el("i", s.icon));
            const titles = el("div");
            titles.append(el("small", null, groupLabels[s.group] || ""), el("h3", null, s.name));
            head.append(icon, titles);
            card.appendChild(head);

            card.appendChild(el("span", "su-level", s.level)).dataset.level = s.level;
            card.appendChild(el("p", "su-about", s.about));

            card.appendChild(el("h4", null, "What I can build"));
            const builds = el("ul", "hp-ticks");
            s.builds.forEach((b) => builds.appendChild(el("li", null, b)));
            card.appendChild(builds);

            card.appendChild(el("h4", null, "Connected skills"));
            const rel = el("div", "su-related");
            s.related.filter((r) => byId[r]).forEach((r) => {
                const b = el("button", null, byId[r].name);
                b.type = "button";
                b.addEventListener("click", () => select(r, true));
                rel.appendChild(b);
            });
            card.appendChild(rel);

            card.appendChild(el("h4", null, "Projects that use it"));
            if (s.projects.length) {
                const list = el("ul", "su-projects");
                s.projects.forEach((p) => {
                    const li = el("li");
                    const a = el("a", null, p.title);
                    a.href = p.url;
                    li.appendChild(a);
                    list.appendChild(li);
                });
                card.appendChild(list);
            } else {
                card.appendChild(el("p", "su-none", "Used behind the scenes in my workflow rather than listed on a specific project."));
            }

            panel.appendChild(card);
        }

        function select(id, focusNode) {
            const s = byId[id];
            if (!s) return;
            selected = id;
            const related = new Set(s.related);
            nodes.forEach((n) => {
                const on = n.dataset.id === id;
                n.classList.toggle("is-selected", on);
                n.classList.toggle("is-related", related.has(n.dataset.id));
                n.setAttribute("aria-pressed", on);
            });
            svg.querySelectorAll("path").forEach((p) => p.classList.toggle("is-on", p.dataset.a === id || p.dataset.b === id));
            showPanel(s);
            if (focusNode) nodeById[id].focus({ preventScroll: true });
        }

        nodes.forEach((n) => n.addEventListener("click", () => select(n.dataset.id)));

        // Area filter
        universe.querySelectorAll(".su-filter").forEach((b) => b.addEventListener("click", () => {
            const g = b.dataset.group;
            universe.querySelectorAll(".su-filter").forEach((x) => {
                x.classList.toggle("is-active", x === b);
                x.setAttribute("aria-pressed", x === b);
            });
            nodes.forEach((n) => n.classList.toggle("is-dim", g !== "all" && n.dataset.group !== g));
            const first = nodes.find((n) => g === "all" || n.dataset.group === g);
            if (first && g !== "all") select(first.dataset.id);
        }));

        select("django");
        drawLines();
        if ("ResizeObserver" in window) new ResizeObserver(() => drawLines()).observe(map);
        else window.addEventListener("resize", drawLines);
        // Fonts and the scroll animation can move nodes slightly after load
        window.addEventListener("load", drawLines);
        setTimeout(drawLines, 1200);
    }

})();
