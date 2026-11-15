/* RU Studio admin: theme toggle (shared with the website) + chart tooltips */

(function () {

    var root = document.documentElement;

    function currentTheme() {
        return root.getAttribute("data-bs-theme") === "light" ? "light" : "dark";
    }

    function setTheme(theme) {
        root.classList.add("rd-theme-switching");
        root.setAttribute("data-bs-theme", theme);
        try {
            localStorage.setItem("theme", theme);
            localStorage.setItem("jazzmin-theme-mode", theme);
        } catch (e) {}
        setTimeout(function () { root.classList.remove("rd-theme-switching"); }, 400);
    }

    /* ---------- Accessibility: name Jazzmin's icon-only buttons ---------- */

    document.querySelectorAll("#jazzy-navbar form button[type='submit']").forEach(function (btn) {
        if (!btn.getAttribute("aria-label")) {
            var input = btn.form && btn.form.querySelector("input[name='q']");
            btn.setAttribute("aria-label", input && input.placeholder ? input.placeholder.replace(/\.+$/, "") : "Search");
        }
    });

    /* ---------- Theme toggle in the top navbar ---------- */

    var navRight = document.querySelector("#jazzy-navbar .navbar-nav.ms-auto");

    if (navRight) {
        var li = document.createElement("li");
        li.className = "nav-item d-flex align-items-center";
        li.innerHTML =
            '<button type="button" class="rd-theme-toggle" title="Switch theme">' +
            '<i class="fas fa-sun"></i><i class="fas fa-moon"></i></button>';
        navRight.insertBefore(li, navRight.firstChild);

        var btn = li.querySelector("button");
        var label = function () {
            btn.setAttribute("aria-label", "Switch to " + (currentTheme() === "dark" ? "light" : "dark") + " mode");
        };
        label();

        btn.addEventListener("click", function () {
            setTheme(currentTheme() === "dark" ? "light" : "dark");
            label();
        });
    }

    /* ---------- Dashboard: hover / focus tooltips ---------- */

    var tip = document.getElementById("rdTooltip");

    if (tip) {
        var show = function (el) {
            var r = el.getBoundingClientRect();
            var bar = el.querySelector(".rd-bar, .rd-hbar-track span") || el;
            var br = bar.getBoundingClientRect();
            tip.textContent = el.getAttribute("data-tip");
            tip.hidden = false;
            tip.style.left = (br.left + br.width / 2) + "px";
            tip.style.top = Math.max(br.top, r.top) + "px";
        };
        var hide = function () { tip.hidden = true; };

        document.querySelectorAll("[data-tip]").forEach(function (el) {
            el.addEventListener("mouseenter", function () { show(el); });
            el.addEventListener("focus", function () { show(el); });
            el.addEventListener("mouseleave", hide);
            el.addEventListener("blur", hide);
        });

        window.addEventListener("scroll", hide, { passive: true });
    }

    /* ---------- Dashboard: chart <-> table toggle ---------- */

    document.querySelectorAll("[data-table-toggle]").forEach(function (btn) {
        var table = document.getElementById(btn.getAttribute("data-table-toggle"));
        if (!table) return;
        btn.setAttribute("aria-pressed", "false");
        btn.addEventListener("click", function () {
            var open = table.hidden;
            table.hidden = !open;
            btn.setAttribute("aria-pressed", String(open));
            btn.querySelector("span").textContent = open ? "Hide table" : "Table";
        });
    });

})();
