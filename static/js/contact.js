/* ==========================================
        CONTACT PAGE INTERACTIONS
========================================== */

(function () {

    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const finePointer = window.matchMedia("(pointer: fine)").matches;

    /* ---------- Local time in Pakistan ---------- */

    const times = document.querySelectorAll(".js-pk-time");
    if (times.length) {
        const fmt = new Intl.DateTimeFormat("en-US", { hour: "numeric", minute: "2-digit", timeZone: "Asia/Karachi" });
        const tick = () => times.forEach((t) => { t.textContent = fmt.format(new Date()); });
        tick();
        setInterval(tick, 30000);
    }

    /* ---------- Copy email / phone ---------- */

    document.querySelectorAll(".ct-copy").forEach((btn) => {
        btn.addEventListener("click", async () => {
            const text = btn.dataset.copy;
            let ok = false;
            try {
                await navigator.clipboard.writeText(text);
                ok = true;
            } catch (e) {
                // Fallback for older browsers / non-secure contexts
                const area = document.createElement("textarea");
                area.value = text;
                area.style.position = "fixed";
                area.style.opacity = "0";
                document.body.append(area);
                area.select();
                try { ok = document.execCommand("copy"); } catch (err) {}
                area.remove();
            }
            const label = btn.querySelector("span");
            const icon = btn.querySelector("i");
            if (!label) return;
            btn.classList.toggle("is-copied", ok);
            label.textContent = ok ? "Copied!" : "Press Ctrl+C";
            if (icon) icon.className = ok ? "fas fa-check" : "far fa-copy";
            setTimeout(() => {
                btn.classList.remove("is-copied");
                label.textContent = "Copy";
                if (icon) icon.className = "far fa-copy";
            }, 1800);
        });
    });

    /* ---------- Spotlight that follows the mouse ---------- */

    if (finePointer) {
        document.querySelectorAll(".ct-spot").forEach((card) => {
            card.addEventListener("pointermove", (e) => {
                const r = card.getBoundingClientRect();
                card.style.setProperty("--mx", `${e.clientX - r.left}px`);
                card.style.setProperty("--my", `${e.clientY - r.top}px`);
            });
        });
    }

    /* ---------- Timeline fills as you scroll ---------- */

    const timeline = document.getElementById("ctTimeline");
    if (timeline) {
        const steps = [...timeline.querySelectorAll("li")];
        const update = () => {
            const r = timeline.getBoundingClientRect();
            const start = window.innerHeight * 0.75;
            const progress = Math.min(1, Math.max(0, (start - r.top) / r.height));
            timeline.style.setProperty("--fill", reduceMotion ? 1 : progress.toFixed(3));
            steps.forEach((li, i) => {
                li.classList.toggle("is-on", reduceMotion || progress >= i / steps.length + 0.02);
            });
        };
        window.addEventListener("scroll", update, { passive: true });
        window.addEventListener("resize", update, { passive: true });
        update();
    }

    /* ---------- Form ---------- */

    const form = document.getElementById("ctForm");

    if (form) {

        const message = form.querySelector("#id_message");
        const count = document.getElementById("ctCount");
        const submit = document.getElementById("ctSubmit");

        const updateCount = () => { if (count && message) count.textContent = message.value.length; };
        message?.addEventListener("input", updateCount);
        updateCount();

        // Live, friendly validation (the server still checks everything).
        const rules = {
            name: (v) => v.trim().length >= 2 || "Please enter your name.",
            email: (v) => /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(v.trim()) || "Please enter a valid email address.",
            subject: (v) => v.trim().length >= 3 || "Please add a short subject.",
            message: (v) => v.trim().length >= 10 || "Tell me a little more (at least 10 characters).",
        };

        const showError = (field, text) => {
            const wrap = field.closest(".ct-field");
            let note = wrap.querySelector(".field-error.js-error");
            wrap.classList.toggle("has-error", !!text);
            wrap.classList.toggle("is-valid", !text && field.value.trim() !== "");
            field.setAttribute("aria-invalid", text ? "true" : "false");
            if (text) {
                if (!note) {
                    note = document.createElement("small");
                    note.className = "field-error js-error";
                    note.id = `${field.id}-error`;
                    wrap.append(note);
                    field.setAttribute("aria-describedby", note.id);
                }
                note.textContent = text;
            } else if (note) {
                note.remove();
            }
        };

        const check = (field) => {
            const rule = rules[field.name];
            if (!rule) return true;
            const result = rule(field.value);
            showError(field, result === true ? "" : result);
            return result === true;
        };

        Object.keys(rules).forEach((name) => {
            const field = form.elements[name];
            if (!field) return;
            field.addEventListener("blur", () => { if (field.value) check(field); });
            field.addEventListener("input", () => {
                if (field.closest(".ct-field").classList.contains("has-error")) check(field);
            });
        });

        form.addEventListener("submit", (e) => {
            const fields = Object.keys(rules).map((n) => form.elements[n]).filter(Boolean);
            const results = fields.map(check);
            const firstBad = fields[results.indexOf(false)];
            if (firstBad) {
                e.preventDefault();
                firstBad.focus();
                return;
            }
            submit.classList.add("is-sending");
            submit.querySelector(".ct-submit-text").textContent = "Sending…";
        });

        // Magnetic button: leans slightly toward the pointer.
        if (finePointer && !reduceMotion && submit) {
            submit.addEventListener("pointermove", (e) => {
                const r = submit.getBoundingClientRect();
                const x = (e.clientX - r.left - r.width / 2) * 0.12;
                const y = (e.clientY - r.top - r.height / 2) * 0.25;
                submit.style.transform = `translate(${x}px, ${y}px)`;
            });
            submit.addEventListener("pointerleave", () => { submit.style.transform = ""; });
        }
    }

    /* ---------- Success: bring the card into view + confetti ---------- */

    const success = document.querySelector(".ct-success");

    if (success) {
        document.getElementById("contact-form")?.scrollIntoView({ behavior: reduceMotion ? "auto" : "smooth", block: "start" });
        if (!reduceMotion) setTimeout(confetti, 600);
    }

    function confetti() {
        const canvas = document.getElementById("ctConfetti");
        if (!canvas) return;
        const ctx = canvas.getContext("2d");
        const dpr = Math.min(window.devicePixelRatio || 1, 2);
        canvas.width = innerWidth * dpr;
        canvas.height = innerHeight * dpr;
        ctx.scale(dpr, dpr);

        const css = getComputedStyle(document.documentElement);
        const colors = [
            css.getPropertyValue("--accent").trim() || "#69d7ff",
            css.getPropertyValue("--accent-2").trim() || "#a5e8ff",
            "#34d399", "#fbbf24", "#ffffff",
        ];

        const pieces = Array.from({ length: 140 }, () => ({
            x: innerWidth / 2 + (Math.random() - 0.5) * 200,
            y: innerHeight * 0.45,
            vx: (Math.random() - 0.5) * 14,
            vy: -Math.random() * 14 - 6,
            size: Math.random() * 7 + 4,
            rot: Math.random() * Math.PI,
            vr: (Math.random() - 0.5) * 0.3,
            color: colors[(Math.random() * colors.length) | 0],
            shape: Math.random() < 0.5 ? "rect" : "circle",
        }));

        const started = performance.now();
        (function frame(now) {
            const t = now - started;
            ctx.clearRect(0, 0, innerWidth, innerHeight);
            pieces.forEach((p) => {
                p.vy += 0.35;
                p.vx *= 0.99;
                p.x += p.vx;
                p.y += p.vy;
                p.rot += p.vr;
                ctx.save();
                ctx.globalAlpha = Math.max(0, 1 - t / 2600);
                ctx.translate(p.x, p.y);
                ctx.rotate(p.rot);
                ctx.fillStyle = p.color;
                if (p.shape === "rect") ctx.fillRect(-p.size / 2, -p.size / 4, p.size, p.size / 2);
                else { ctx.beginPath(); ctx.arc(0, 0, p.size / 2.4, 0, Math.PI * 2); ctx.fill(); }
                ctx.restore();
            });
            if (t < 2600) requestAnimationFrame(frame);
            else ctx.clearRect(0, 0, innerWidth, innerHeight);
        })(started);
    }

})();
