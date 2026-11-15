/* ==========================================
        WEBSITE PRICE ESTIMATOR
   Prices come from ESTIMATOR_PRICES in base/views.py
========================================== */

(function () {

    const form = document.getElementById("estimator");
    const dataTag = document.getElementById("estimator-prices");

    if (!form || !dataTag) return;

    const prices = JSON.parse(dataTag.textContent);

    const el = {
        pages: document.getElementById("estPages"),
        pagesOut: document.getElementById("estPagesOut"),
        price: document.getElementById("estPrice"),
        days: document.getElementById("estDays"),
        pagesSummary: document.getElementById("estPagesSummary"),
        summary: document.getElementById("estSummary"),
        quote: document.getElementById("estQuote"),
        whatsapp: document.getElementById("estWhatsapp"),
        rush: document.getElementById("estRush"),
    };

    const byId = (list, id) => list.find(item => item.id === id);

    const rupees = (n) => "Rs " + Math.round(n).toLocaleString("en-PK");

    // Round to a friendly number, e.g. 43,750 -> 44,000
    const roundNice = (n) => Math.round(n / 1000) * 1000;

    function budgetBucket(total) {
        if (total < 25000) return "under_25k";
        if (total < 50000) return "25k_50k";
        if (total < 100000) return "50k_100k";
        return "100k_plus";
    }

    let lastType = null;

    function calculate() {

        const type = byId(prices.types, form.type.value);

        // When the website type changes, suggest its usual page count.
        if (type.id !== lastType) {
            if (lastType !== null) el.pages.value = type.pages;
            lastType = type.id;
        }

        const pages = +el.pages.value;
        const design = byId(prices.designs, form.design.value);
        const features = [...form.querySelectorAll("input[name=features]:checked")]
            .map(input => byId(prices.features, input.value));
        const rush = el.rush.checked;

        // ----- Price -----
        const extraPages = Math.max(0, pages - type.pages);

        let total = type.base + extraPages * prices.extra_page;
        features.forEach(f => total += f.price);
        total *= design.multiplier;
        if (rush) total *= prices.rush_multiplier;

        const low = roundNice(total * 0.9);
        const high = roundNice(total * 1.15);

        // ----- Time -----
        let days = type.days + Math.ceil(extraPages / 2);
        features.forEach(f => days += f.days);
        if (design.multiplier > 1) days = Math.ceil(days * 1.2);
        if (rush) days = Math.ceil(days * 0.65);

        const weeks = Math.max(1, Math.round(days / 7));
        const timeText = days <= 7 ? `About ${days} days` : `About ${weeks} week${weeks > 1 ? "s" : ""}`;

        // ----- Render -----
        el.pagesOut.textContent = `${pages} page${pages > 1 ? "s" : ""}`;
        el.price.textContent = `${rupees(low)} – ${rupees(high)}`;
        el.days.textContent = timeText;
        el.pagesSummary.textContent = el.pagesOut.textContent;

        const lines = [type.label, `${design.label} design`, ...features.map(f => f.label)];
        if (rush) lines.push("Priority delivery");

        el.summary.replaceChildren(...lines.map(text => {
            const li = document.createElement("li");
            li.textContent = text;
            return li;
        }));

        // ----- Pre-fill the contact form & WhatsApp -----
        const message =
            `Hi Rana, I used your price estimator.\n\n` +
            `Website: ${type.label}\n` +
            `Pages: ${pages}\n` +
            `Design: ${design.label}\n` +
            `Features: ${features.length ? features.map(f => f.label).join(", ") : "None"}\n` +
            `Urgent: ${rush ? "Yes" : "No"}\n` +
            `Estimate: ${rupees(low)} - ${rupees(high)}\n\n` +
            `About my business: `;

        const params = new URLSearchParams({
            type: type.id,
            budget: budgetBucket(total),
            subject: `Quote for ${type.label}`,
            message: message,
        });

        el.quote.href = `${el.quote.pathname}?${params}#contact-form`;
        el.whatsapp.href = `https://wa.me/923238144826?text=${encodeURIComponent(message)}`;

    }

    form.addEventListener("input", calculate);
    form.addEventListener("change", calculate);

    calculate();

})();
