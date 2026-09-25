/* ==========================================
        RANA UMAR PORTFOLIO
========================================== */

const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;


document.addEventListener("DOMContentLoaded", () => {

    /* ==========================================
            SCROLL ANIMATIONS (AOS)
    ========================================== */

    // Sections without their own animation fade up as a whole.
    document.querySelectorAll("section:not(.hero-section)").forEach(section => {

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
            NAVBAR + BACK TO TOP (on scroll)
    ========================================== */

    const navbar = document.querySelector(".navbar");
    const backToTop = document.getElementById("backToTop");

    function onScroll() {

        navbar.classList.toggle("scrolled", window.scrollY > 50);

        if (backToTop) {
            backToTop.style.display = window.scrollY > 300 ? "flex" : "none";
        }

    }

    window.addEventListener("scroll", onScroll, { passive: true });

    onScroll();

    if (backToTop) {

        backToTop.addEventListener("click", () => {
            window.scrollTo({ top: 0, behavior: "smooth" });
        });

    }



    /* ==========================================
            TYPING ANIMATION
    ========================================== */

    const typingText = document.querySelector(".typing-text");

    const words = [
        "Full Stack Developer",
        "Website Designer",
        "Django Developer",
        "Python Developer"
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
            PROJECT FILTER
    ========================================== */

    const filterButtons = document.querySelectorAll(".filter-btn");
    const projectItems = document.querySelectorAll(".project-item");

    filterButtons.forEach(button => {

        button.addEventListener("click", () => {

            filterButtons.forEach(btn => btn.classList.remove("active"));
            button.classList.add("active");

            const filter = button.dataset.filter;

            projectItems.forEach(project => {
                const show = filter === "all" || project.classList.contains(filter);
                project.style.display = show ? "block" : "none";
            });

        });

    });

});



/* ==========================================
        PAGE LOADER
========================================== */

window.addEventListener("load", () => {

    const loader = document.getElementById("loader");

    if (!loader) return;

    loader.classList.add("loaded");

    setTimeout(() => loader.remove(), 600);

});
