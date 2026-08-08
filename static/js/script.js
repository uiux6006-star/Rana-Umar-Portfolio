/* ==========================================
        RANA UMAR PORTFOLIO
========================================== */

document.addEventListener("DOMContentLoaded", () => {

    /* ==========================================
            PRELOADER
========================================== */

const preloader = document.getElementById("preloader");

window.addEventListener("load", () => {

    setTimeout(() => {

        preloader.style.opacity = "0";

        preloader.style.visibility = "none";

    }, 2200);

});

    /* ==========================================
            NAVBAR SCROLL EFFECT
    ========================================== */

    const navbar = document.querySelector(".navbar");

    window.addEventListener("scroll", () => {

        if (window.scrollY > 50) {

            navbar.style.background = "rgba(0,0,0,.95)";
            navbar.style.padding = "12px 0";

        } else {

            navbar.style.background = "rgba(0,0,0,.85)";
            navbar.style.padding = "18px 0";

        }

    });



    /* ==========================================
            SMOOTH SCROLL
    ========================================== */

    document.querySelectorAll('a[href^="#"]').forEach(anchor => {

        anchor.addEventListener("click", function (e) {

            const target = document.querySelector(this.getAttribute("href"));

            if (target) {

                e.preventDefault();

                target.scrollIntoView({

                    behavior: "smooth"

                });

            }

        });

    });



    /* ==========================================
            ACTIVE NAVBAR LINK
    ========================================== */

   

    /* ==========================================
            SCROLL REVEAL
    ========================================== */

    const revealElements = document.querySelectorAll("section");

    function revealOnScroll() {

        revealElements.forEach(section => {

            const windowHeight = window.innerHeight;

            const revealTop = section.getBoundingClientRect().top;

            const revealPoint = 100;

            if (revealTop < windowHeight - revealPoint) {

                section.style.opacity = "1";
                section.style.transform = "translateY(0)";

            }

        });

    }

    revealElements.forEach(section => {

        section.style.opacity = "0";
        section.style.transform = "translateY(50px)";
        section.style.transition = "all .8s ease";

    });

    window.addEventListener("scroll", revealOnScroll);

    revealOnScroll();
    /* ==========================================
        TYPING ANIMATION
========================================== */

const typingText = document.querySelector(".typing-text");

const words = [

    "Full Stack Developer",
    "Python Developer",
    "Django Developer",
    "Frontend Developer",
    "UI Designer"

];

let wordIndex = 0;
let charIndex = 0;
let isDeleting = false;

function typeEffect() {

    if (!typingText) return;

    const currentWord = words[wordIndex];

    if (isDeleting) {

        typingText.textContent = currentWord.substring(0, charIndex--);

    } else {

        typingText.textContent = currentWord.substring(0, charIndex++);

    }

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

typeEffect();



/* ==========================================
        BACK TO TOP BUTTON
========================================== */

const backToTop = document.getElementById("backToTop");

window.addEventListener("scroll", () => {

    if (!backToTop) return;

    if (window.scrollY > 300) {

        backToTop.style.display = "flex";

    } else {

        backToTop.style.display = "none";

    }

});

if (backToTop) {

    backToTop.addEventListener("click", () => {

        window.scrollTo({

            top: 0,
            behavior: "smooth"

        });

    });

}



/* ==========================================
        COUNTER ANIMATION
========================================== */

const counters = document.querySelectorAll(".counter");

counters.forEach(counter => {

    counter.innerText = "0";

    const updateCounter = () => {

        const target = +counter.getAttribute("data-target");

        const current = +counter.innerText;

        const increment = target / 100;

        if (current < target) {

            counter.innerText = `${Math.ceil(current + increment)}`;

            setTimeout(updateCounter, 20);

        } else {

            counter.innerText = target;

        }

    };

    updateCounter();

});



/* ==========================================
        SKILL BAR ANIMATION
========================================== */

const progressBars = document.querySelectorAll(".progress-bar");

progressBars.forEach(bar => {

    const width = bar.getAttribute("aria-valuenow");

    bar.style.width = "0%";

    setTimeout(() => {

        bar.style.width = width + "%";

    }, 500);

});

});


/* ==========================================
            CUSTOM CURSOR
========================================== */

const cursorDot = document.querySelector(".cursor-dot");
const cursorOutline = document.querySelector(".cursor-outline");

document.addEventListener("mousemove", (e) => {

    if (!cursorDot || !cursorOutline) return;

    cursorDot.style.left = e.clientX + "px";
    cursorDot.style.top = e.clientY + "px";

    cursorOutline.style.left = e.clientX + "px";
    cursorOutline.style.top = e.clientY + "px";

});

/* ==========================================
            MOUSE GLOW
========================================== */

const cursorGlow = document.querySelector(".cursor-glow");

document.addEventListener("mousemove", (e) => {

    if (!cursorGlow) return;

    cursorGlow.style.left = e.clientX + "px";
    cursorGlow.style.top = e.clientY + "px";

});

/* ==========================================
        PROJECT FILTER
========================================== */

const filterButtons = document.querySelectorAll(".filter-btn");
const projects = document.querySelectorAll(".project-item");

filterButtons.forEach(button => {

    button.addEventListener("click", () => {

        filterButtons.forEach(btn => btn.classList.remove("active"));
        button.classList.add("active");

        const filter = button.dataset.filter;

        projects.forEach(project => {

            if (filter === "all") {

                project.style.display = "block";

            } else if (project.classList.contains(filter)) {

                project.style.display = "block";

            } else {

                project.style.display = "none";

            }

        });

    });

});
window.onload=function(){

document.getElementById("loader").style.display="none";

}


