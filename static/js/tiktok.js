/* ==========================================
        FROM MY TIKTOK
   TikTok's player only loads when a visitor presses play, so the page
   stays fast and no TikTok cookies are set before that.
========================================== */

(function () {

    "use strict";

    document.querySelectorAll(".tt-media[data-player]").forEach((media) => {
        const button = media.querySelector(".tt-play");
        if (!button) return;

        button.addEventListener("click", () => {
            const frame = document.createElement("iframe");
            frame.src = media.dataset.player;
            frame.title = media.dataset.title || "TikTok video";
            frame.allow = "autoplay; encrypted-media; fullscreen; picture-in-picture";
            frame.allowFullscreen = true;
            frame.referrerPolicy = "strict-origin-when-cross-origin";
            media.classList.add("is-playing");
            media.textContent = "";
            media.appendChild(frame);
            frame.focus();
        });
    });

})();
