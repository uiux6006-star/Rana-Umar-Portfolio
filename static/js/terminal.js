/* ==========================================
        RUD TERMINAL
   A real, keyboard-driven terminal. Every [data-terminal] element on the
   page becomes one (the home page has an inline one; the overlay works on
   every page). Data comes from /terminal/data/, loaded on first use.

   Output is always built with textContent / DOM nodes, never innerHTML.
========================================== */

(function (root) {

    "use strict";

    /* ---------- Commands (pure: input + data -> lines) ---------- */

    // A line is { parts: [string | {text, href, external, cls}], cls }
    const line = (...parts) => ({ parts });
    const styled = (cls, ...parts) => ({ parts, cls });
    const link = (text, href, external) => ({ text, href, external: !!external });
    const pad = (text, n) => (text + " ".repeat(n)).slice(0, Math.max(n, text.length + 1));

    const HELP = [
        ["about", "Learn about Rana Umar"],
        ["whoami", "Who's behind this site"],
        ["skills", "Explore technical skills"],
        ["projects", "View development projects"],
        ["open <n>", "Open project number n"],
        ["experience", "Work experience"],
        ["education", "Education and courses"],
        ["journey", "The learning journey"],
        ["services", "Explore services"],
        ["github", "Open GitHub profile"],
        ["contact", "Contact the developer"],
        ["cv", "Download CV"],
        ["theme", "Switch dark / light mode"],
        ["history", "Commands you've typed"],
        ["clear", "Clear terminal"],
    ];

    const COMMANDS = HELP.map(([name]) => name.split(" ")[0]).concat(["help", "exit", "date", "echo", "sudo", "hire", "coffee", "rud", "ls", "pwd", "konami"]);

    function run(input, data, ctx) {
        const raw = String(input || "").trim();
        if (!raw) return { lines: [] };

        const [cmdRaw, ...args] = raw.split(/\s+/);
        const cmd = cmdRaw.toLowerCase();
        const out = [];
        const result = { lines: out };

        if (!data && !["help", "clear", "exit", "date", "echo", "history", "theme"].includes(cmd)) {
            out.push(styled("t-warn", "Still loading profile data... try again in a second."));
            return result;
        }

        switch (cmd) {

            case "help":
                out.push(styled("t-dim", "Available commands:"));
                out.push(line(""));
                HELP.forEach(([name, text]) => out.push(line({ text: pad(name, 13), cls: "t-cmd" }, text)));
                out.push(line(""));
                out.push(styled("t-dim", "Tip: Tab completes, ↑/↓ browse history. Some commands are hidden…"));
                break;

            case "about":
                out.push(styled("t-title", `${data.name} — ${data.role}`));
                out.push(line(data.summary));
                out.push(line(""));
                out.push(line({ text: "Location  ", cls: "t-dim" }, data.location));
                out.push(line({ text: "Next goal ", cls: "t-dim" }, data.future));
                out.push(line({ text: "More      ", cls: "t-dim" }, link("/about", data.urls.about)));
                break;

            case "whoami":
                out.push(line({ text: "visitor", cls: "t-cmd" }, " — you, exploring the portfolio of"));
                out.push(styled("t-title", `${data.brand}`));
                out.push(line(`${data.role} · ${data.future} · ${data.location}`));
                break;

            case "skills":
                data.skills.forEach((group) => {
                    out.push(styled("t-title", group.group));
                    group.items.forEach((s) => out.push(line("  ", { text: pad(s.name, 30), cls: "t-cmd" }, { text: s.level, cls: "t-dim" })));
                });
                out.push(line(""));
                out.push(line({ text: "Explore the interactive Skills Universe: ", cls: "t-dim" }, link("/about#skills", data.urls.about + "#skills")));
                break;

            case "projects":
            case "ls": {
                const query = args.join(" ").toLowerCase();
                const list = data.projects.filter((p) => !query ||
                    (p.title + " " + p.kind + " " + p.tech.join(" ")).toLowerCase().includes(query));
                out.push(styled("t-dim", query ? `Projects matching "${query}":` : `${data.projects.length} projects:`));
                list.forEach((p) => {
                    const n = data.projects.indexOf(p) + 1;
                    out.push(line(
                        { text: String(n).padStart(2, "0") + "  ", cls: "t-dim" },
                        link(p.title, p.url),
                        { text: `  ${p.kind}${p.live ? " · live" : ""}`, cls: "t-dim" }
                    ));
                });
                if (!list.length) out.push(styled("t-warn", "No projects match that."));
                out.push(line(""));
                out.push(styled("t-dim", "Type 'open 1' to open a project, or 'projects django' to filter."));
                break;
            }

            case "open": {
                const n = parseInt(args[0], 10);
                const p = data.projects[n - 1];
                if (!p) {
                    out.push(styled("t-warn", `Usage: open <1-${data.projects.length}>`));
                } else {
                    out.push(line("Opening ", link(p.title, p.url), " …"));
                    result.navigate = p.url;
                }
                break;
            }

            case "experience":
                data.experience.forEach((e) => {
                    out.push(styled("t-title", e.role));
                    out.push(styled("t-dim", `${e.when} · ${e.where}`));
                    e.points.forEach((pt) => out.push(line("  • " + pt)));
                });
                break;

            case "education":
                data.education.forEach((e) => {
                    out.push(line({ text: e.title, cls: "t-cmd" }, { text: `  ${e.when}`, cls: "t-dim" }));
                    out.push(line("  " + e.where));
                });
                out.push(line(""));
                out.push(line(link("View the full CV", data.cv, true)));
                break;

            case "journey":
                data.journey.forEach((j, i) => {
                    out.push(line({ text: (i ? "  ↓ " : "  ● "), cls: "t-cmd" }, j.title, { text: j.skills.length ? `  (${j.skills.join(", ")})` : "", cls: "t-dim" }));
                });
                break;

            case "services":
                data.services.forEach((s) => {
                    out.push(styled("t-title", s.name));
                    out.push(line("  " + s.text));
                });
                out.push(line(""));
                out.push(line({ text: "Plan your project: ", cls: "t-dim" }, link("/estimate", data.urls.planner)));
                break;

            case "github":
                out.push(line("Opening ", link(data.contact.github, data.contact.github, true), " …"));
                result.open = data.contact.github;
                break;

            case "contact":
                out.push(styled("t-title", "Let's build something great."));
                out.push(line({ text: "Email     ", cls: "t-dim" }, link(data.contact.email, "mailto:" + data.contact.email)));
                out.push(line({ text: "WhatsApp  ", cls: "t-dim" }, link("Chat on WhatsApp", data.contact.whatsapp, true)));
                out.push(line({ text: "LinkedIn  ", cls: "t-dim" }, link("rana-umar", data.contact.linkedin, true)));
                out.push(line({ text: "Form      ", cls: "t-dim" }, link("/contact", data.contact.page)));
                break;

            case "cv":
                out.push(line("Downloading CV… ", link("Rana_Umar_CV.pdf", data.cv, true)));
                result.download = data.cv;
                break;

            case "theme":
                out.push(styled("t-dim", "Switching theme…"));
                result.theme = true;
                break;

            case "history":
                (ctx && ctx.history || []).forEach((h, i) => out.push(line({ text: String(i + 1).padStart(3, " ") + "  ", cls: "t-dim" }, h)));
                break;

            case "date":
                out.push(line(new Date().toString()));
                break;

            case "echo":
                out.push(line(args.join(" ")));
                break;

            case "pwd":
                out.push(line("/home/visitor/rud"));
                break;

            case "clear":
                result.clear = true;
                break;

            case "exit":
                result.exit = true;
                out.push(styled("t-dim", "Bye! Press ` any time to come back."));
                break;

            /* ---------- Easter eggs ---------- */

            case "sudo":
                if (args.join(" ").toLowerCase().replace(/\s+/g, "-") === "hire-rana" || args[0] === "hire") {
                    out.push(styled("t-ok", "[sudo] permission granted. Excellent decision."));
                    out.push(line("Opening the project planner so we can get started → ", link("/estimate", data.urls.planner)));
                } else {
                    out.push(styled("t-warn", "visitor is not in the sudoers file. This incident will be reported… to Rana. 😄"));
                    out.push(styled("t-dim", "Hint: try 'sudo hire rana'"));
                }
                break;

            case "hire":
                out.push(styled("t-ok", "Great choice! Let's talk about your project."));
                out.push(line(link("Start on the contact page", data.contact.page), "  or  ", link("WhatsApp", data.contact.whatsapp, true)));
                break;

            case "coffee":
                out.push(line("    ( (     "));
                out.push(line("     ) )    "));
                out.push(line("  ........  "));
                out.push(line("  |      |] "));
                out.push(line("  \\      /  "));
                out.push(line("   `----'   "));
                out.push(styled("t-dim", "Code runs on coffee. Brewing a fresh cup for your project…"));
                break;

            case "rud":
                out.push(styled("t-title", " ____  _   _ ____  "));
                out.push(styled("t-title", "|  _ \\| | | |  _ \\ "));
                out.push(styled("t-title", "| |_) | | | | | | |"));
                out.push(styled("t-title", "|  _ <| |_| | |_| |"));
                out.push(styled("t-title", "|_| \\_\\\\___/|____/ "));
                out.push(styled("t-dim", "BUILD • CODE • INNOVATE"));
                break;

            case "konami":
                out.push(styled("t-dim", "↑ ↑ ↓ ↓ ← → ← → B A … try it on the page, not in here 😉"));
                break;

            default:
                out.push(styled("t-warn", `command not found: ${cmdRaw}`));
                out.push(styled("t-dim", "Type 'help' to see what I can do."));
        }

        return result;
    }

    function complete(partial) {
        const p = String(partial || "").toLowerCase();
        if (!p) return [];
        return COMMANDS.filter((c, i, all) => c.startsWith(p) && all.indexOf(c) === i);
    }

    const api = { run, complete, COMMANDS };

    // Node (tests) gets the pure functions only
    if (typeof module !== "undefined" && module.exports) {
        module.exports = api;
        return;
    }


    /* ---------- Browser ---------- */

    const reduceMotion = root.matchMedia("(prefers-reduced-motion: reduce)").matches;
    let dataPromise = null;

    function loadData(url) {
        if (!dataPromise) {
            dataPromise = fetch(url, { headers: { Accept: "application/json" } })
                .then((r) => { if (!r.ok) throw new Error(r.status); return r.json(); })
                .catch(() => { dataPromise = null; return null; });
        }
        return dataPromise;
    }

    function render(lineSpec) {
        const el = document.createElement("div");
        el.className = "t-line" + (lineSpec.cls ? " " + lineSpec.cls : "");
        lineSpec.parts.forEach((part) => {
            if (typeof part === "string") {
                el.appendChild(document.createTextNode(part));
            } else if (part.href) {
                const a = document.createElement("a");
                a.href = part.href;
                a.textContent = part.text;
                if (part.external) { a.target = "_blank"; a.rel = "noopener"; }
                el.appendChild(a);
            } else {
                const span = document.createElement("span");
                if (part.cls) span.className = part.cls;
                span.textContent = part.text;
                el.appendChild(span);
            }
        });
        if (!lineSpec.parts.length || (lineSpec.parts.length === 1 && lineSpec.parts[0] === "")) el.innerHTML = "&nbsp;";
        return el;
    }

    class Terminal {

        constructor(el) {
            this.el = el;
            this.screen = el.querySelector(".t-screen");
            this.output = el.querySelector(".t-output");
            this.form = el.querySelector(".t-form");
            this.input = el.querySelector(".t-input");
            this.dataUrl = el.dataset.terminal;
            this.history = [];
            this.cursor = 0;
            this.data = null;
            this.busy = false;

            this.form.addEventListener("submit", (e) => { e.preventDefault(); this.submit(this.input.value); });
            this.input.addEventListener("keydown", (e) => this.onKey(e));
            this.screen.addEventListener("click", (e) => {
                if (!e.target.closest("a") && !getSelection().toString()) this.input.focus({ preventScroll: true });
            });
            el.querySelectorAll("[data-run]").forEach((b) => b.addEventListener("click", () => {
                this.submit(b.dataset.run);
                this.input.focus({ preventScroll: true });
            }));
        }

        async boot() {
            if (this.booted) return;
            this.booted = true;
            const intro = [
                styled("t-dim", "RUD OS v2.0 — Rana Umar Developer"),
                line("Welcome! Type ", { text: "help", cls: "t-cmd" }, " to see what you can explore."),
            ];
            await this.print(intro);
            loadData(this.dataUrl).then((d) => { this.data = d; });
        }

        async submit(value) {
            const text = String(value || "").trim();
            this.input.value = "";
            this.echo(text);
            if (!text) return;

            this.history.push(text);
            this.cursor = this.history.length;

            if (!this.data) this.data = await loadData(this.dataUrl);
            const result = run(text, this.data, { history: this.history });

            if (result.clear) { this.output.textContent = ""; return; }
            await this.print(result.lines);

            if (result.theme) document.getElementById("themeToggle")?.click();
            if (result.open) root.open(result.open, "_blank", "noopener");
            if (result.download) {
                const a = document.createElement("a");
                a.href = result.download; a.download = ""; document.body.appendChild(a); a.click(); a.remove();
            }
            if (result.navigate) setTimeout(() => { root.location.href = result.navigate; }, 450);
            if (result.exit) this.el.dispatchEvent(new CustomEvent("terminal:exit", { bubbles: true }));
        }

        echo(text) {
            const el = document.createElement("div");
            el.className = "t-line t-echo";
            const prompt = document.createElement("span");
            prompt.className = "t-prompt";
            prompt.textContent = "visitor@rud:~$ ";
            el.append(prompt, document.createTextNode(text));
            this.output.appendChild(el);
            this.scroll();
        }

        async print(lines) {
            for (const spec of lines) {
                this.output.appendChild(render(spec));
                this.scroll();
                if (!reduceMotion && lines.length < 40) await new Promise((r) => setTimeout(r, 14));
            }
        }

        scroll() {
            this.screen.scrollTop = this.screen.scrollHeight;
        }

        onKey(e) {
            if (e.key === "ArrowUp") {
                e.preventDefault();
                if (this.cursor > 0) this.input.value = this.history[--this.cursor];
            } else if (e.key === "ArrowDown") {
                e.preventDefault();
                if (this.cursor < this.history.length - 1) this.input.value = this.history[++this.cursor];
                else { this.cursor = this.history.length; this.input.value = ""; }
            } else if (e.key === "Tab") {
                const matches = complete(this.input.value.trim());
                if (matches.length === 1) {
                    e.preventDefault();
                    this.input.value = matches[0] + " ";
                } else if (matches.length > 1) {
                    e.preventDefault();
                    this.echo(this.input.value);
                    this.print([styled("t-dim", matches.join("   "))]);
                }
            } else if (e.key === "l" && e.ctrlKey) {
                e.preventDefault();
                this.output.textContent = "";
            }
        }
    }

    /* ---------- Wire up ---------- */

    const terminals = new Map();

    function init(el) {
        if (terminals.has(el)) return terminals.get(el);
        const t = new Terminal(el);
        terminals.set(el, t);
        return t;
    }

    // Inline terminals boot when they scroll into view
    document.querySelectorAll("[data-terminal]:not(.t-overlay-box)").forEach((el) => {
        const t = init(el);
        if ("IntersectionObserver" in root) {
            const io = new IntersectionObserver((entries) => {
                if (entries.some((en) => en.isIntersecting)) { t.boot(); io.disconnect(); }
            }, { threshold: 0.3 });
            io.observe(el);
        } else {
            t.boot();
        }
    });

    // Overlay terminal (every page)
    const overlay = document.getElementById("rudTerminal");
    if (overlay) {
        const box = overlay.querySelector("[data-terminal]");
        const t = init(box);
        let lastFocus = null;

        const open = () => {
            if (!overlay.hidden) return;
            lastFocus = document.activeElement;
            overlay.hidden = false;
            document.body.classList.add("t-open");
            requestAnimationFrame(() => overlay.classList.add("is-open"));
            t.boot();
            setTimeout(() => t.input.focus(), 60);
        };
        const close = () => {
            overlay.classList.remove("is-open");
            document.body.classList.remove("t-open");
            setTimeout(() => { overlay.hidden = true; }, reduceMotion ? 0 : 220);
            if (lastFocus && lastFocus.focus) lastFocus.focus();
        };

        document.querySelectorAll("[data-open-terminal]").forEach((b) => b.addEventListener("click", open));
        overlay.querySelectorAll("[data-close-terminal]").forEach((b) => b.addEventListener("click", close));
        overlay.addEventListener("terminal:exit", () => setTimeout(close, 500));
        overlay.addEventListener("click", (e) => { if (e.target === overlay) close(); });

        document.addEventListener("keydown", (e) => {
            const typing = /^(INPUT|TEXTAREA|SELECT)$/.test(document.activeElement.tagName) || document.activeElement.isContentEditable;
            if ((e.key === "`" || e.key === "~") && !typing) { e.preventDefault(); open(); }
            else if (e.key === "Escape" && !overlay.hidden) close();
            else if (e.key === "Tab" && !overlay.hidden && !e.defaultPrevented) {
                // Keep focus inside the dialog
                const items = [...overlay.querySelectorAll("button, input, a[href]")].filter((n) => n.offsetParent);
                if (!items.length) return;
                const first = items[0], last = items[items.length - 1];
                if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
                else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
            }
        });

        root.RUD = Object.assign(root.RUD || {}, { openTerminal: open });
    }

})(typeof window !== "undefined" ? window : globalThis);
