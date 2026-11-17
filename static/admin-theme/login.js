/* Admin login: show/hide password, caps-lock hint, loading state, starfield. */

(function () {

    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    /* ---------- Show / hide password ---------- */

    const eye = document.getElementById("lgEye");
    const password = document.getElementById("id_password");

    if (eye && password) {
        eye.addEventListener("click", () => {
            const show = password.type === "password";
            password.type = show ? "text" : "password";
            eye.setAttribute("aria-pressed", String(show));
            eye.setAttribute("aria-label", show ? "Hide password" : "Show password");
            eye.querySelector("i").className = show ? "far fa-eye-slash" : "far fa-eye";
            password.focus();
        });

        const caps = document.getElementById("lgCaps");
        const checkCaps = (e) => {
            if (caps && e.getModifierState) caps.hidden = !e.getModifierState("CapsLock");
        };
        password.addEventListener("keydown", checkCaps);
        password.addEventListener("keyup", checkCaps);
        password.addEventListener("blur", () => { if (caps) caps.hidden = true; });
    }

    /* ---------- Loading state on submit ---------- */

    const form = document.getElementById("login-form");
    const submit = document.getElementById("lgSubmit");

    if (form && submit) {
        form.addEventListener("submit", (e) => {
            const user = form.elements.username.value.trim();
            const pass = form.elements.password.value;
            if (!user || !pass) {
                e.preventDefault();
                (user ? form.elements.password : form.elements.username).focus();
                return;
            }
            submit.classList.add("is-loading");
            submit.querySelector("i").className = "fas fa-circle-notch";
            submit.querySelector("span").textContent = "Signing in…";
        });
    }

    /* ---------- Twinkling starfield ---------- */

    const canvas = document.getElementById("lgStars");
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    let stars = [];
    let width = 0, height = 0;

    function resize() {
        const dpr = Math.min(window.devicePixelRatio || 1, 2);
        width = window.innerWidth;
        height = window.innerHeight;
        canvas.width = width * dpr;
        canvas.height = height * dpr;
        ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
        const count = Math.round((width * height) / 9000);
        stars = Array.from({ length: count }, () => ({
            x: Math.random() * width,
            y: Math.random() * height,
            r: Math.random() < 0.9 ? Math.random() * 1.1 + 0.2 : Math.random() * 1.8 + 1,
            phase: Math.random() * Math.PI * 2,
            speed: 0.4 + Math.random() * 1.2,
            hue: Math.random() < 0.3 ? "170, 220, 255" : "255, 255, 255",
        }));
    }

    function draw(t) {
        ctx.clearRect(0, 0, width, height);
        for (const s of stars) {
            const a = reduceMotion ? 0.6 : 0.35 + 0.45 * (0.5 + 0.5 * Math.sin(t / 1000 * s.speed + s.phase));
            ctx.fillStyle = `rgba(${s.hue}, ${a})`;
            ctx.beginPath();
            ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
            ctx.fill();
        }
        if (!reduceMotion) requestAnimationFrame(draw);
    }

    resize();
    window.addEventListener("resize", resize, { passive: true });
    requestAnimationFrame(draw);

})();
