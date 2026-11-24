/* ==========================================
        EASTER EGGS (optional, never in the way)
   - Konami code  ↑ ↑ ↓ ↓ ← → ← → B A  -> developer mode
   - Click the logo 5 times quickly     -> hidden message
   - A note for developers in the console
========================================== */

(function () {

    "use strict";

    let toastTimer = null;

    function toast(icon, text) {
        let el = document.querySelector(".rud-egg");
        if (!el) {
            el = document.createElement("div");
            el.className = "rud-egg";
            el.setAttribute("role", "status");
            el.innerHTML = '<i aria-hidden="true"></i><span></span>';
            document.body.appendChild(el);
        }
        el.querySelector("i").className = "fas " + icon;
        el.querySelector("span").textContent = text;
        requestAnimationFrame(() => el.classList.add("is-on"));
        clearTimeout(toastTimer);
        toastTimer = setTimeout(() => el.classList.remove("is-on"), 4200);
    }

    /* ---------- Konami code ---------- */

    const code = ["arrowup", "arrowup", "arrowdown", "arrowdown", "arrowleft", "arrowright", "arrowleft", "arrowright", "b", "a"];
    let pos = 0;

    document.addEventListener("keydown", (e) => {
        if (/^(INPUT|TEXTAREA|SELECT)$/.test(document.activeElement.tagName)) return;
        const key = (e.key || "").toLowerCase();
        pos = key === code[pos] ? pos + 1 : (key === code[0] ? 1 : 0);
        if (pos === code.length) {
            pos = 0;
            const on = document.documentElement.classList.toggle("rud-devmode");
            toast("fa-terminal", on
                ? "Developer mode unlocked. Press ` to open the RUD terminal."
                : "Developer mode off. See you next time, fellow dev.");
        }
    });

    /* ---------- Logo clicks ---------- */

    const logo = document.querySelector(".sn-logo");
    if (logo) {
        let clicks = 0;
        let timer = null;
        logo.addEventListener("click", (e) => {
            clicks += 1;
            clearTimeout(timer);
            timer = setTimeout(() => { clicks = 0; }, 1200);
            if (clicks >= 5) {
                e.preventDefault();
                clicks = 0;
                toast("fa-code", "You found it! Built with Django, coffee and a lot of curiosity. — Rana");
            }
        });
    }

    /* ---------- Console ---------- */

    try {
        console.log(
            "%c RUD %c Rana Umar Developer \n\nHello, fellow developer 👋\nLike what you see? Type `sudo hire rana` in the terminal (press ` on any page).\n",
            "background:#69d7ff;color:#07101c;font-weight:800;padding:4px 6px;border-radius:4px",
            "color:#69d7ff;font-weight:700"
        );
    } catch (e) { /* console may be unavailable */ }

})();
