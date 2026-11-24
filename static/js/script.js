/* ==========================================
        RANA UMAR PORTFOLIO
========================================== */

const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;


document.addEventListener("DOMContentLoaded", () => {

    /* ==========================================
            LIGHT / DARK THEME TOGGLE
       The theme is first set by a small script in <head>.
    ========================================== */

    const root = document.documentElement;
    const themeToggle = document.getElementById("themeToggle");

    function syncThemeButton() {
        if (!themeToggle) return;
        const next = root.getAttribute("data-bs-theme") === "dark" ? "light" : "dark";
        themeToggle.setAttribute("aria-label", `Switch to ${next} mode`);
    }

    if (themeToggle) {

        themeToggle.addEventListener("click", () => {

            const next = root.getAttribute("data-bs-theme") === "dark" ? "light" : "dark";

            root.classList.add("theme-switching");
            root.setAttribute("data-bs-theme", next);
            setTimeout(() => root.classList.remove("theme-switching"), 450);

            try { localStorage.setItem("theme", next); } catch (e) {}

            syncThemeButton();

        });

        syncThemeButton();

    }

    // Follow the system setting until the visitor picks a theme themselves.
    const systemLight = window.matchMedia("(prefers-color-scheme: light)");

    systemLight.addEventListener?.("change", (e) => {
        let saved = null;
        try { saved = localStorage.getItem("theme"); } catch (err) {}
        if (saved) return;
        root.setAttribute("data-bs-theme", e.matches ? "light" : "dark");
        syncThemeButton();
    });



    /* ==========================================
            NAVBAR: sliding highlight behind links
    ========================================== */

    const snLinks = document.querySelector(".sn-links");

    if (snLinks) {

        const indicator = snLinks.querySelector(".sn-indicator");
        const links = [...snLinks.querySelectorAll(".sn-link")];
        const active = snLinks.querySelector(".sn-link.is-active");

        const moveTo = (link) => {
            if (!link) {
                indicator.style.opacity = "0";
                return;
            }
            indicator.style.opacity = "1";
            indicator.style.width = `${link.offsetWidth}px`;
            indicator.style.transform = `translateX(${link.offsetLeft}px)`;
        };

        // Place it without animating on first paint.
        indicator.style.transition = "none";
        moveTo(active);
        requestAnimationFrame(() => indicator.style.transition = "");

        links.forEach(link => {
            link.addEventListener("mouseenter", () => moveTo(link));
            link.addEventListener("focus", () => moveTo(link));
        });

        snLinks.addEventListener("mouseleave", () => moveTo(active));
        window.addEventListener("resize", () => moveTo(active), { passive: true });
        document.fonts?.ready.then(() => moveTo(active));

    }



    /* ==========================================
            MOBILE MENU (full screen)
    ========================================== */

    const burger = document.getElementById("snBurger");
    const menu = document.getElementById("snMenu");

    if (burger && menu) {

        const setMenu = (open) => {
            burger.setAttribute("aria-expanded", String(open));
            burger.setAttribute("aria-label", open ? "Close menu" : "Open menu");
            root.classList.toggle("sn-open", open);

            if (open) {
                menu.hidden = false;
                requestAnimationFrame(() => menu.classList.add("is-open"));
                menu.querySelector("a")?.focus({ preventScroll: true });
            } else {
                menu.classList.remove("is-open");
                setTimeout(() => { if (!menu.classList.contains("is-open")) menu.hidden = true; }, prefersReducedMotion ? 0 : 450);
            }
        };

        burger.addEventListener("click", () => setMenu(burger.getAttribute("aria-expanded") !== "true"));

        menu.addEventListener("click", (e) => {
            if (e.target.closest("a")) setMenu(false);
        });

        document.addEventListener("keydown", (e) => {
            if (e.key === "Escape" && root.classList.contains("sn-open")) {
                setMenu(false);
                burger.focus();
            }
        });

        // Close if the window grows to desktop size.
        window.matchMedia("(min-width: 1100px)").addEventListener?.("change", (e) => {
            if (e.matches) setMenu(false);
        });

    }



    /* ==========================================
            FOOTER: local time + back to top
    ========================================== */

    const clock = document.getElementById("sfClock");

    if (clock) {
        const fmt = new Intl.DateTimeFormat("en-US", {
            hour: "numeric", minute: "2-digit", timeZone: "Asia/Karachi"
        });
        const updateClock = () => { clock.textContent = `${fmt.format(new Date())} PKT`; };
        updateClock();
        setInterval(updateClock, 30000);
    }

    document.getElementById("sfTop")?.addEventListener("click", (e) => {
        e.preventDefault();
        window.scrollTo({ top: 0, behavior: prefersReducedMotion ? "auto" : "smooth" });
    });



    /* ==========================================
            HERO ROBOT (tilts toward the pointer)
    ========================================== */

    const robot = document.getElementById("robotFigure");

    if (robot && !prefersReducedMotion && window.matchMedia("(pointer: fine)").matches) {

        const stage = robot.closest(".hero-section") || document.body;

        stage.addEventListener("mousemove", (e) => {
            const rect = robot.getBoundingClientRect();
            const x = (e.clientX - (rect.left + rect.width / 2)) / window.innerWidth;
            const y = (e.clientY - (rect.top + rect.height / 2)) / window.innerHeight;
            robot.style.transform = `perspective(900px) rotateY(${x * 18}deg) rotateX(${-y * 10}deg)`;
        });

        stage.addEventListener("mouseleave", () => {
            robot.style.transform = "";
        });

    }

    // Click (or Enter / Space) makes the robot do a full 360° spin.
    if (robot && !prefersReducedMotion) {

        const spin = () => {
            if (robot.classList.contains("is-spinning")) return;
            robot.classList.add("is-spinning");
        };

        robot.addEventListener("click", spin);
        robot.addEventListener("keydown", (e) => {
            if (e.key === "Enter" || e.key === " ") {
                e.preventDefault();
                spin();
            }
        });

        robot.querySelector(".robot-spin")?.addEventListener("animationend", (e) => {
            if (e.animationName === "robotSpin360") robot.classList.remove("is-spinning");
        });

    }


    /* ==========================================
            SCROLL ANIMATIONS (AOS)
    ========================================== */

    // Sections without their own animation fade up as a whole.
    document.querySelectorAll("section:not(.hero-section):not(.no-aos)").forEach(section => {

        if (!section.querySelector("[data-aos]")) {
            section.setAttribute("data-aos", "fade-up");
        }

    });

    if (window.AOS) {

        AOS.init({
            duration: 800,
            easing: "ease-out-cubic",
            once: true,
            offset: 60,
            disable: prefersReducedMotion
        });

    }



    /* ==========================================
            NAVBAR + SCROLL PROGRESS (on scroll)
    ========================================== */

    const navbar = document.getElementById("siteNav");
    const scrollProgress = document.getElementById("scrollProgress");

    function onScroll() {

        const y = window.scrollY;

        // The navbar always stays fixed at the top; it just turns more solid once you scroll.
        if (navbar) {
            navbar.classList.toggle("is-scrolled", y > 30);
        }

        if (scrollProgress) {
            const max = document.documentElement.scrollHeight - window.innerHeight;
            scrollProgress.style.transform = `scaleX(${max > 0 ? Math.min(window.scrollY / max, 1) : 0})`;
        }

    }

    window.addEventListener("scroll", onScroll, { passive: true });

    onScroll();



    /* ==========================================
            TYPING ANIMATION
    ========================================== */

    const typingText = document.querySelector(".typing-text");

    const words = [
        "Web Developer",
        "Website Designer",
        "Django Developer",
        "Future Python Developer"
    ];

    let wordIndex = 0;
    let charIndex = 0;
    let isDeleting = false;

    function typeEffect() {

        const currentWord = words[wordIndex];

        typingText.textContent = currentWord.substring(0, isDeleting ? charIndex-- : charIndex++);

        let speed = isDeleting ? 60 : 120;

        if (!isDeleting && charIndex === currentWord.length + 1) {
            speed = 1500;
            isDeleting = true;
        }

        if (isDeleting && charIndex === 0) {
            isDeleting = false;
            wordIndex = (wordIndex + 1) % words.length;
        }

        setTimeout(typeEffect, speed);

    }

    if (typingText && !prefersReducedMotion) {
        typeEffect();
    }



    /* ==========================================
            COUNTER ANIMATION (starts when visible)
    ========================================== */

    const counters = document.querySelectorAll(".counter");

    function animateCounter(counter) {

        const target = +counter.dataset.target;
        const duration = 1600;
        const start = performance.now();

        const step = (now) => {

            const progress = Math.min((now - start) / duration, 1);
            const eased = 1 - Math.pow(1 - progress, 3);

            counter.innerText = Math.round(target * eased);

            if (progress < 1) requestAnimationFrame(step);

        };

        requestAnimationFrame(step);

    }

    if (counters.length && "IntersectionObserver" in window && !prefersReducedMotion) {

        const counterObserver = new IntersectionObserver((entries) => {

            entries.forEach(entry => {

                if (entry.isIntersecting) {
                    animateCounter(entry.target);
                    counterObserver.unobserve(entry.target);
                }

            });

        }, { threshold: 0.6 });

        counters.forEach(counter => {
            counter.innerText = "0";
            counterObserver.observe(counter);
        });

    }



    /* ==========================================
            HERO MOUSE PARALLAX
    ========================================== */

    const hero = document.querySelector(".hero-v2");

    if (hero && !prefersReducedMotion && window.matchMedia("(pointer: fine)").matches) {

        const layers = hero.querySelectorAll("[data-depth]");

        hero.addEventListener("mousemove", (e) => {

            const rect = hero.getBoundingClientRect();
            const x = (e.clientX - rect.left) / rect.width - 0.5;
            const y = (e.clientY - rect.top) / rect.height - 0.5;

            layers.forEach(layer => {
                const depth = +layer.dataset.depth;
                layer.style.translate = `${x * depth}px ${y * depth}px`;
            });

        });

        hero.addEventListener("mouseleave", () => {
            layers.forEach(layer => layer.style.translate = "0 0");
        });

    }



    /* ==========================================
            CUSTOM CURSOR
    ========================================== */

    const cursorParts = document.querySelectorAll(".cursor-dot, .cursor-outline, .cursor-glow");

    document.addEventListener("mousemove", (e) => {

        document.body.classList.add("cursor-ready");

        cursorParts.forEach(part => {
            part.style.left = e.clientX + "px";
            part.style.top = e.clientY + "px";
        });

    });



    /* ==========================================
            PROJECT GALLERY LIGHTBOX
    ========================================== */

    const galleryItems = [...document.querySelectorAll(".gallery-item")];
    const lightbox = document.getElementById("lightbox");

    if (galleryItems.length && lightbox) {

        const lightboxImg = lightbox.querySelector("img");
        const lightboxCaption = lightbox.querySelector("figcaption");
        let current = 0;

        const show = (index) => {
            current = (index + galleryItems.length) % galleryItems.length;
            const item = galleryItems[current];
            lightboxImg.src = item.dataset.full;
            lightboxImg.alt = item.dataset.caption || "";
            lightboxCaption.textContent = item.dataset.caption || "";
        };

        const open = (index) => {
            show(index);
            lightbox.hidden = false;
            document.body.style.overflow = "hidden";
        };

        const close = () => {
            lightbox.hidden = true;
            document.body.style.overflow = "";
            galleryItems[current].focus();
        };

        galleryItems.forEach((item, index) => item.addEventListener("click", () => open(index)));

        lightbox.querySelector(".lightbox-close").addEventListener("click", close);
        lightbox.querySelector(".lightbox-prev").addEventListener("click", () => show(current - 1));
        lightbox.querySelector(".lightbox-next").addEventListener("click", () => show(current + 1));

        lightbox.addEventListener("click", (e) => {
            if (e.target === lightbox) close();
        });

        document.addEventListener("keydown", (e) => {
            if (lightbox.hidden) return;
            if (e.key === "Escape") close();
            if (e.key === "ArrowLeft") show(current - 1);
            if (e.key === "ArrowRight") show(current + 1);
        });

    }

});



/* ==========================================
        PRELOADER
   Plays once per visit. Counts to 100% while the page loads,
   then lifts away. Never blocks the page for more than ~4s.
========================================== */

(function () {

    const loader = document.getElementById("loader");
    const root = document.documentElement;

    if (!loader) return;

    if (root.classList.contains("rl-skip")) {
        loader.remove();
        return;
    }

    const bar = document.getElementById("rlBar");
    const count = document.getElementById("rlCount");
    const started = performance.now();
    const minShow = prefersReducedMotion ? 0 : 1100;   // long enough to read the name
    let progress = 0;
    let finished = false;
    let raf;

    root.classList.add("rl-active");

    function paint() {
        if (bar) bar.style.transform = `scaleX(${progress / 100})`;
        if (count) count.textContent = Math.round(progress);
    }

    // Ease toward 90% while loading; the last 10% waits for the load event.
    function tick() {
        if (!finished) {
            progress += (90 - progress) * 0.045;
            paint();
            raf = requestAnimationFrame(tick);
        }
    }

    function finish() {
        if (finished) return;
        finished = true;
        cancelAnimationFrame(raf);

        const wait = Math.max(0, minShow - (performance.now() - started));

        setTimeout(() => {
            progress = 100;
            paint();

            setTimeout(() => {
                loader.classList.add("is-done");
                root.classList.remove("rl-active");
                try { sessionStorage.setItem("rl-seen", "1"); } catch (e) {}
                setTimeout(() => loader.remove(), prefersReducedMotion ? 0 : 1000);
            }, prefersReducedMotion ? 0 : 260);
        }, wait);
    }

    tick();

    if (document.readyState === "complete") {
        finish();
    } else {
        window.addEventListener("load", finish);
    }

    setTimeout(finish, 4000);   // safety net for slow third-party assets

})();
