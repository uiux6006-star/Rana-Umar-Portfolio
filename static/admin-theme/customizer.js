/* Theme Customizer: instant preview, search/filter, accent picker. */

(function () {

    function readJSON(id) {
        var el = document.getElementById(id);
        return el ? JSON.parse(el.textContent) : null;
    }

    var tokens = readJSON("tc-tokens");
    var activeSlug = readJSON("tc-active");
    var activeAccent = readJSON("tc-active-accent") || "";

    var stage = document.getElementById("tcStage");
    if (!tokens || !stage) return;

    var nameEl = document.getElementById("tcPreviewName");
    var liveForm = document.getElementById("tcLiveForm");
    var applyForm = document.getElementById("tcApplyForm");
    var applyBtn = document.getElementById("tcApplyBtn");
    var picker = document.getElementById("tcAccentPicker");
    var hexInput = document.getElementById("tcAccentHex");
    var contrastNote = document.getElementById("tcContrast");

    var state = { slug: activeSlug, mode: "dark", accent: activeAccent };

    /* ---------- colour helpers (mirror appearance/themes.py) ---------- */

    function hexToRgb(hex) {
        hex = hex.replace("#", "");
        return [0, 2, 4].map(function (i) { return parseInt(hex.substr(i, 2), 16); });
    }

    function rgbToHex(rgb) {
        return "#" + rgb.map(function (c) {
            var v = Math.max(0, Math.min(255, Math.round(c))).toString(16);
            return v.length === 1 ? "0" + v : v;
        }).join("");
    }

    function mix(a, b, t) {
        var ra = hexToRgb(a), rb = hexToRgb(b);
        return rgbToHex(ra.map(function (x, i) { return x + (rb[i] - x) * t; }));
    }

    function lum(hex) {
        return hexToRgb(hex).map(function (c) {
            c /= 255;
            return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
        }).reduce(function (sum, c, i) { return sum + c * [0.2126, 0.7152, 0.0722][i]; }, 0);
    }

    function contrast(a, b) {
        var la = lum(a), lb = lum(b);
        return (Math.max(la, lb) + 0.05) / (Math.min(la, lb) + 0.05);
    }

    function darkenUntil(color, against, ratio) {
        var step = 0, out = color;
        while (contrast(out, against) < ratio && step < 1) {
            step += 0.04;
            out = mix(color, "#000000", step);
        }
        return out;
    }

    function isHex(v) { return /^#[0-9a-fA-F]{6}$/.test(v); }

    /* ---------- render the stage ---------- */

    function render() {
        var t = tokens[state.slug];
        var vars = Object.assign({}, t.shared, t[state.mode]);

        if (state.accent && isHex(state.accent)) {
            var primary = state.mode === "light" ? darkenUntil(state.accent, "#ffffff", 4.5) : state.accent;
            var rgb = hexToRgb(primary).join(" ");
            vars["--accent"] = primary;
            vars["--accent-2"] = state.mode === "light" ? primary : mix(state.accent, "#ffffff", 0.3);
            vars["--accent-rgb"] = rgb;
            vars["--glow-rgb"] = hexToRgb(state.accent).join(" ");
            vars["--glow"] = "rgb(" + rgb + " / .16)";
            vars["--on-accent"] = contrast(primary, "#07101c") >= contrast(primary, "#ffffff") ? "#07101c" : "#ffffff";
        }

        Object.keys(vars).forEach(function (name) {
            if (name.indexOf("--") === 0) stage.style.setProperty(name, vars[name]);
        });
        stage.setAttribute("data-theme", state.slug);

        var card = document.querySelector('.tc-card[data-slug="' + state.slug + '"] h2');
        if (nameEl && card) {
            nameEl.textContent = card.textContent + (state.accent ? " · accent " + state.accent : "");
        }

        document.querySelectorAll(".tc-card").forEach(function (c) {
            c.classList.toggle("is-previewing", c.getAttribute("data-slug") === state.slug);
        });

        // Keep the action forms pointed at what is being previewed.
        [liveForm, applyForm].forEach(function (form) {
            if (!form) return;
            form.querySelector('[name="theme"]').value = state.slug;
            form.querySelector('[name="accent"]').value = state.accent || "";
        });

        if (applyBtn) {
            var live = state.slug === activeSlug && (state.accent || "") === activeAccent;
            applyBtn.disabled = live;
            applyBtn.querySelector("span").textContent = live
                ? "Already live"
                : "Apply " + (card ? card.textContent : "theme");
        }
    }

    /* ---------- preview buttons ---------- */

    document.querySelectorAll("[data-preview]").forEach(function (btn) {
        btn.addEventListener("click", function () {
            var slug = btn.getAttribute("data-preview");
            if (slug !== state.slug) state.accent = slug === activeSlug ? activeAccent : "";
            state.slug = slug;
            render();
            if (window.innerWidth < 1280) {
                stage.scrollIntoView({ behavior: "smooth", block: "center" });
            }
        });
    });

    document.querySelectorAll(".tc-mode button").forEach(function (btn) {
        btn.addEventListener("click", function () {
            state.mode = btn.getAttribute("data-mode");
            document.querySelectorAll(".tc-mode button").forEach(function (b) {
                var on = b === btn;
                b.classList.toggle("is-active", on);
                b.setAttribute("aria-pressed", String(on));
            });
            render();
        });
    });

    /* ---------- accent picker ---------- */

    function onAccent(value) {
        if (!isHex(value)) return;
        state.slug = activeSlug;   // the accent form applies to the live theme
        state.accent = value.toLowerCase();
        render();

        if (contrastNote) {
            var surface = tokens[activeSlug].dark["--bg"];
            var ratio = contrast(value, surface);
            contrastNote.className = "tc-contrast " + (ratio >= 3 ? "is-good" : "is-warn");
            contrastNote.textContent = ratio >= 3
                ? "✓ Good contrast on the dark background (" + ratio.toFixed(1) + ":1). Light mode is adjusted automatically."
                : "⚠ Low contrast on the dark background (" + ratio.toFixed(1) + ":1). Try a brighter colour.";
        }
    }

    if (picker && hexInput) {
        picker.addEventListener("input", function () {
            hexInput.value = picker.value;
            onAccent(picker.value);
        });
        hexInput.addEventListener("input", function () {
            var v = hexInput.value.trim();
            if (v && v[0] !== "#") v = "#" + v;
            if (isHex(v)) {
                picker.value = v.toLowerCase();
                onAccent(v);
            }
        });
    }

    /* ---------- search + filter ---------- */

    var search = document.getElementById("tcSearch");
    var empty = document.getElementById("tcEmpty");
    var filter = "all";

    function applyFilter() {
        var q = search ? search.value.trim().toLowerCase() : "";
        var shown = 0;
        document.querySelectorAll(".tc-card").forEach(function (card) {
            var tags = card.getAttribute("data-tags").split(" ");
            var ok = (filter === "all" || tags.indexOf(filter) !== -1) &&
                     (!q || card.getAttribute("data-name").indexOf(q) !== -1);
            card.hidden = !ok;
            if (ok) shown++;
        });
        if (empty) empty.hidden = shown > 0;
    }

    if (search) search.addEventListener("input", applyFilter);

    document.querySelectorAll(".tc-chip").forEach(function (chip) {
        chip.addEventListener("click", function () {
            filter = chip.getAttribute("data-filter");
            document.querySelectorAll(".tc-chip").forEach(function (c) {
                c.classList.toggle("is-active", c === chip);
            });
            applyFilter();
        });
    });

    render();

})();
