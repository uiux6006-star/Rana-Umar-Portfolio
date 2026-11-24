/* ==========================================
        GITHUB ACTIVITY CENTRE
   Fills #ghHub from /github/data/ (fetched and cached on the server).
   If GitHub is unavailable, shows a fallback. Never shows made-up data.
========================================== */

(function () {

    "use strict";

    const hub = document.getElementById("ghHub");
    if (!hub) return;

    const $ = (name) => hub.querySelector(`[data-gh="${name}"]`);

    const LANG_COLORS = {
        Python: "#3572A5", HTML: "#e34c26", CSS: "#563d7c", JavaScript: "#f1e05a",
        TypeScript: "#3178c6", SCSS: "#c6538c", Shell: "#89e051", Jupyter: "#DA5B0B",
    };

    const el = (tag, cls, text) => {
        const n = document.createElement(tag);
        if (cls) n.className = cls;
        if (text != null) n.textContent = text;
        return n;
    };

    function ago(iso) {
        const then = new Date(iso);
        if (isNaN(then)) return "";
        const s = Math.max(0, (Date.now() - then) / 1000);
        if (s < 3600) return `${Math.max(1, Math.round(s / 60))} min ago`;
        if (s < 86400) return `${Math.round(s / 3600)} h ago`;
        const d = Math.round(s / 86400);
        if (d < 30) return `${d} day${d === 1 ? "" : "s"} ago`;
        return then.toLocaleDateString(undefined, { month: "short", day: "numeric", year: "numeric" });
    }

    function fallback() {
        hub.setAttribute("aria-busy", "false");
        hub.classList.add("is-offline");
        $("fallback").hidden = false;
        $("list").hidden = true;
        $("status").textContent = "Live data unavailable";
        $("grid").closest(".gh-activity").hidden = true;
    }

    function render(data) {
        const p = data.profile;

        if (p.avatar) {
            const img = el("img");
            img.src = p.avatar;
            img.alt = `${p.login} on GitHub`;
            img.width = 88; img.height = 88; img.loading = "lazy";
            const box = hub.querySelector(".gh-avatar");
            box.textContent = "";
            box.appendChild(img);
        }
        if (p.bio) $("bio").textContent = p.bio;
        $("repos").textContent = p.public_repos;
        $("followers").textContent = p.followers;
        $("following").textContent = p.following;

        // Languages
        if (data.languages.length) {
            const langs = $("langs");
            const bar = langs.querySelector(".gh-langbar");
            const list = langs.querySelector("ul");
            data.languages.forEach((l) => {
                const color = LANG_COLORS[l.name] || "var(--accent)";
                const seg = el("span");
                seg.style.width = l.percent + "%";
                seg.style.background = color;
                bar.appendChild(seg);
                const li = el("li");
                const dot = el("i"); dot.style.background = color;
                li.append(dot, el("span", null, l.name), el("small", null, `${l.percent}%`));
                list.appendChild(li);
            });
            langs.hidden = false;
        }

        // Activity grid: one column per week, oldest first
        const grid = $("grid");
        const max = Math.max(1, ...data.activity.map((d) => d.count));
        data.activity.forEach((d) => {
            const cell = el("span");
            const level = d.count === 0 ? 0 : Math.min(4, Math.ceil((d.count / max) * 4));
            cell.className = "gh-cell l" + level;
            cell.title = `${d.count} contribution${d.count === 1 ? "" : "s"} on ${d.date}`;
            grid.appendChild(cell);
        });
        grid.setAttribute("aria-label", `${data.activity_total} public contributions in the last 12 weeks`);
        $("note").textContent = data.activity_total
            ? `${data.activity_total} public contributions in the last 12 weeks, from the GitHub API.`
            : "No public activity in the last 12 weeks. Most recent work may be in private repositories.";

        $("status").textContent = "";
        $("status").append(el("span", "gh-pulse"), document.createTextNode(` Live · updated ${ago(data.fetched_at)}`));

        // Repositories
        const list = $("list");
        list.textContent = "";
        data.repos.forEach((r, i) => {
            const card = el("article", "gh-repo hp-spot");
            card.style.setProperty("--i", i);

            const head = el("div", "gh-repo-head");
            head.append(el("i", "fas fa-book-bookmark"));
            const name = el("a", "gh-repo-name", r.name);
            name.href = r.url; name.target = "_blank"; name.rel = "noopener";
            head.appendChild(name);
            card.appendChild(head);

            card.appendChild(el("p", "gh-repo-desc", r.description || "No description yet."));

            const meta = el("div", "gh-repo-meta");
            if (r.language) {
                const lang = el("span");
                const dot = el("i"); dot.style.background = LANG_COLORS[r.language] || "var(--accent)";
                lang.append(dot, document.createTextNode(r.language));
                meta.appendChild(lang);
            }
            if (r.stars) meta.appendChild(el("span", null, `★ ${r.stars}`));
            if (r.pushed_at) meta.appendChild(el("span", null, `Updated ${ago(r.pushed_at)}`));
            card.appendChild(meta);

            const links = el("div", "gh-repo-links");
            const code = el("a", null, "Code");
            code.href = r.url; code.target = "_blank"; code.rel = "noopener";
            links.appendChild(code);
            if (r.homepage && /^https?:\/\//.test(r.homepage)) {
                const live = el("a", null, "Live site");
                live.href = r.homepage; live.target = "_blank"; live.rel = "noopener";
                links.appendChild(live);
            }
            card.appendChild(links);

            list.appendChild(card);
        });

        hub.setAttribute("aria-busy", "false");
        hub.classList.add("is-ready");
    }

    function load() {
        fetch(hub.dataset.src, { headers: { Accept: "application/json" } })
            .then((r) => (r.ok ? r.json() : null))
            .then((data) => (data && data.ok ? render(data) : fallback()))
            .catch(fallback);
    }

    // Load when the section is close to the viewport
    if ("IntersectionObserver" in window) {
        const io = new IntersectionObserver((entries) => {
            if (entries.some((e) => e.isIntersecting)) { io.disconnect(); load(); }
        }, { rootMargin: "400px" });
        io.observe(hub);
    } else {
        load();
    }

})();
