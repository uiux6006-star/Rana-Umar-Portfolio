/* ==========================================
        RUD ASSISTANT: free FAQ chatbot
   - Understands simple English and Roman Urdu questions.
   - Every answer comes from /chat/knowledge/ (the site's own data).
   - Can collect a lead (name, email, message) into Leads / Enquiries.
   - Conversation survives page changes (sessionStorage).
========================================== */

(function () {

    const root = document.getElementById("chatbot");
    if (!root) return;

    const $ = (id) => document.getElementById(id);
    const panel = $("cbPanel"), body = $("cbBody"), quick = $("cbQuick");
    const form = $("cbForm"), input = $("cbText"), launcher = $("cbLauncher");
    const teaser = $("cbTeaser"), badge = $("cbBadge");
    const html = document.documentElement;

    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const STORE = "rud-chat-v1";

    let kb = null;            // knowledge, loaded on first use
    let state = load() || { log: [], flow: null, lead: {}, chips: null };
    let busy = false;

    /* ---------- storage ---------- */

    function load() {
        try { return JSON.parse(sessionStorage.getItem(STORE)); } catch (e) { return null; }
    }

    function save() {
        try {
            state.log = state.log.slice(-60);
            sessionStorage.setItem(STORE, JSON.stringify(state));
        } catch (e) {}
    }

    /* ---------- helpers ---------- */

    const rs = (n) => "Rs " + Number(n).toLocaleString("en-PK");

    function el(tag, cls, text) {
        const node = document.createElement(tag);
        if (cls) node.className = cls;
        if (text != null) node.textContent = text;
        return node;
    }

    function link(text, href, cls, external) {
        const a = el("a", cls || "cb-link", text);
        a.href = href;
        if (external) { a.target = "_blank"; a.rel = "noopener"; }
        return a;
    }

    async function getKnowledge() {
        if (kb) return kb;
        const res = await fetch(root.dataset.knowledgeUrl, { headers: { "Accept": "application/json" } });
        if (!res.ok) throw new Error("knowledge " + res.status);
        kb = await res.json();
        return kb;
    }

    function waLink(text) {
        return `${kb.whatsapp}?text=${encodeURIComponent(text || "Hi Rana, I found you through your website chat.")}`;
    }

    /* ---------- rendering ---------- */

    function scrollDown() {
        body.scrollTo({ top: body.scrollHeight, behavior: reduceMotion ? "auto" : "smooth" });
    }

    function addBubble(from, node, persist = true) {
        const row = el("div", `cb-row cb-${from}`);
        const bubble = el("div", "cb-bubble");
        if (typeof node === "string") bubble.textContent = node;
        else bubble.append(node);
        row.append(bubble);
        body.append(row);
        if (persist) {
            // User text is stored as plain text; bot HTML is built only from safe DOM nodes.
            state.log.push(from === "user" ? { from, text: bubble.textContent } : { from, html: bubble.innerHTML });
            save();
        }
        scrollDown();
    }

    function setChips(chips) {
        state.chips = chips;
        save();
        quick.replaceChildren(...(chips || []).map((c) => {
            const b = el("button", "cb-chip", c.label);
            b.type = "button";
            b.addEventListener("click", () => handleUser(c.label, c.intent));
            return b;
        }));
    }

    function typing() {
        const row = el("div", "cb-row cb-bot cb-typing-row");
        const dots = el("div", "cb-bubble cb-typing");
        dots.append(el("i"), el("i"), el("i"));
        dots.setAttribute("aria-label", "Assistant is typing");
        row.append(dots);
        body.append(row);
        scrollDown();
        return row;
    }

    async function say(nodes, chips) {
        const list = Array.isArray(nodes) ? nodes : [nodes];
        for (const n of list) {
            const t = typing();
            const length = typeof n === "string" ? n.length : n.textContent.length;
            await new Promise((r) => setTimeout(r, reduceMotion ? 0 : 380 + Math.min(600, length * 6)));
            t.remove();
            addBubble("bot", n);
        }
        setChips(chips);
    }

    function restoreLog() {
        body.replaceChildren();
        state.log.forEach((m) => {
            const row = el("div", `cb-row cb-${m.from}`);
            const bubble = el("div", "cb-bubble");
            if (m.from === "user") bubble.textContent = m.text;
            else bubble.innerHTML = m.html;
            row.append(bubble);
            body.append(row);
        });
        setChips(state.chips);
        body.scrollTop = body.scrollHeight;
    }

    /* ---------- standard chips ---------- */

    const MAIN = [
        { label: "💰 Prices", intent: "price" },
        { label: "⏱️ Timeline", intent: "timeline" },
        { label: "💼 Services", intent: "services" },
        { label: "🗂️ See projects", intent: "projects" },
        { label: "📩 Leave my details", intent: "lead" },
        { label: "💬 Talk to Rana", intent: "contact" },
    ];

    const after = (...first) => {
        const seen = new Set(first.map((c) => c.intent));
        return [...first, ...MAIN.filter((c) => !seen.has(c.intent))].slice(0, 5);
    };

    /* ---------- answers ---------- */

    function p(text) { return el("p", null, text); }

    function card(title, rows, footer) {
        const box = el("div");
        if (title) box.append(el("p", "cb-card-title", title));
        const ul = el("ul", "cb-list");
        rows.forEach((r) => {
            const li = el("li");
            if (r.strong) li.append(el("strong", null, r.strong));
            if (r.value) li.append(el("span", "cb-val", r.value));
            if (r.text) li.append(el("small", null, r.text));
            ul.append(li);
        });
        box.append(ul);
        if (footer) box.append(footer);
        return box;
    }

    const TYPE_WORDS = {
        ecommerce: /(e-?commerce|online store|store|shop|dukaan|dukan|cart|products?)/,
        webapp: /(web ?app|system|management|dashboard|portal|crm|erp|software)/,
        landing: /(landing|portfolio|one[- ]page|single page)/,
        business: /(business|company|brand|corporate|clinic|school|restaurant)/,
    };

    function typeFromText(t) {
        for (const id of Object.keys(TYPE_WORDS)) if (TYPE_WORDS[id].test(t)) return id;
        return null;
    }

    function priceFor(id) {
        const t = kb.prices.find((x) => x.id === id);
        if (!t) return answers.price();
        state.lead.project_type = id;
        save();
        const weeks = Math.max(1, Math.round(t.days / 7));
        const box = el("div");
        box.append(
            p(`${/^[aeiou]/i.test(t.label) ? "An" : "A"} ${t.label.toLowerCase()} starts from ${rs(t.from)}.`),
            p(`It usually takes around ${t.days <= 7 ? t.days + " days" : weeks + " week" + (weeks > 1 ? "s" : "")}, depending on pages and features.`),
            link("Get an exact estimate →", kb.urls.estimate, "cb-btn"),
        );
        return say(box, after({ label: "📩 Get a quote", intent: "lead" }, { label: "➕ Extra features", intent: "features" }));
    }

    const answers = {

        greet() {
            return say(p("Hi! 👋 I'm Rana's website assistant. What would you like to know?"), MAIN);
        },

        price() {
            const rows = kb.prices.map((t) => ({ strong: t.label, value: "from " + rs(t.from) }));
            return say([
                card("Starting prices", rows),
                p("The final price depends on pages, features and design. There are no hidden charges."),
            ], [
                ...kb.prices.map((t) => ({ label: t.label, intent: "type:" + t.id })),
                { label: "🧮 Open estimator", intent: "estimator" },
            ]);
        },

        features() {
            const rows = kb.features.map((f) => ({ strong: f.label, value: "+ " + rs(f.price) }));
            return say(card("Popular extras", rows, link("Add them in the estimator →", kb.urls.estimate, "cb-btn")),
                after({ label: "📩 Get a quote", intent: "lead" }));
        },

        estimator() {
            const box = el("div");
            box.append(
                p("The price estimator lets you pick your website type, pages and features and see a price range instantly."),
                link("Open the estimator →", kb.urls.estimate, "cb-btn"),
            );
            return say(box, after({ label: "📩 Get a quote", intent: "lead" }));
        },

        timeline() {
            const rows = kb.prices.map((t) => {
                const w = Math.max(1, Math.round(t.days / 7));
                return { strong: t.label, value: t.days <= 7 ? `~${t.days} days` : `~${w} week${w > 1 ? "s" : ""}` };
            });
            return say([card("Typical timelines", rows), p(kb.faqs.timeline)], after({ label: "💰 Prices", intent: "price" }));
        },

        services() {
            const rows = kb.services.map((s) => ({ strong: s.name, text: s.text }));
            return say(card("What I can build for you", rows, link("See all services →", kb.urls.services, "cb-link")),
                after({ label: "💰 Prices", intent: "price" }));
        },

        projects() {
            const box = el("div");
            box.append(el("p", "cb-card-title", `Recent work (${kb.project_count} projects)`));
            const list = el("div", "cb-projects");
            kb.projects.slice(0, 4).forEach((pr) => {
                const a = link("", pr.url, "cb-project");
                const tags = [...new Set([pr.category, ...pr.tech])].slice(0, 4);
                a.append(el("strong", null, pr.title), el("small", null, tags.join(" · ")));
                list.append(a);
            });
            box.append(list, link("View all projects →", kb.urls.projects, "cb-link"));
            return say(box, after({ label: "💰 Prices", intent: "price" }));
        },

        process() {
            const rows = kb.process.map((s, i) => ({ strong: `${i + 1}. ${s.name}`, text: s.text }));
            return say(card("How we'll work together", rows), after({ label: "⏱️ Timeline", intent: "timeline" }));
        },

        mobile() { return say(p(kb.faqs.mobile), after()); },
        admin() { return say(p(kb.faqs.admin), after({ label: "➕ Extra features", intent: "features" })); },
        support() { return say(p(kb.faqs.support), after()); },

        seo() {
            const f = kb.features.find((x) => /seo/i.test(x.label));
            return say(p(`Yes. I can set up the SEO basics (page titles, descriptions, sitemap, Google-friendly speed)${f ? " for " + rs(f.price) : ""} so customers can find you on Google.`), after({ label: "💰 Prices", intent: "price" }));
        },

        payment() {
            const f = kb.features.find((x) => /payment/i.test(x.label));
            return say(p(`Yes, I can add online payments like JazzCash, Easypaisa and cards${f ? " (" + "+ " + rs(f.price) + ")" : ""}.`), after({ label: "🛒 Online store price", intent: "type:ecommerce" }));
        },

        hosting() {
            const f = kb.features.find((x) => /hosting/i.test(x.label));
            return say(p(`Yes. I can set up your domain and hosting and put the site live${f ? " (+ " + rs(f.price) + ")" : ""}. I'll guide you on the best option for your budget.`), after());
        },

        urdu() {
            const f = kb.features.find((x) => /urdu/i.test(x.label));
            return say(p(`Yes. Your website can have English and Urdu versions${f ? " (+ " + rs(f.price) + ")" : ""}. And you can talk to me in English or Urdu. 🙂`), after());
        },

        tech() {
            return say(p(`I mainly build with ${kb.tech.slice(0, 6).join(", ")}. For 3D experiences I use Three.js. I pick the right tool for your project, not the other way round.`), after({ label: "🗂️ See projects", intent: "projects" }));
        },

        location() {
            return say(p(`I'm based in ${kb.location} and work with clients anywhere, online.`), after({ label: "💬 Talk to Rana", intent: "contact" }));
        },

        cv() {
            const box = el("div");
            box.append(p("Here's my CV:"), link("Download CV →", kb.urls.cv, "cb-btn"));
            return say(box, after());
        },

        contact() {
            const box = el("div");
            box.append(
                p("You can reach Rana directly:"),
                link("Chat on WhatsApp", waLink(), "cb-btn cb-btn-wa", true),
                link(kb.email, "mailto:" + kb.email, "cb-link"),
            );
            return say(box, [{ label: "📩 Leave my details", intent: "lead" }, { label: "💰 Prices", intent: "price" }]);
        },

        thanks() { return say(p("You're welcome! Anything else I can help with?"), MAIN); },

        fallback() {
            return say([
                p("I'm not sure I understood that. I can answer questions about prices, timelines, services and projects."),
                p("Or leave your details and Rana will reply personally."),
            ], MAIN);
        },

        /* ----- lead capture ----- */

        lead() {
            state.flow = "lead_name";
            save();
            return say(p("Great! What's your name?"), [{ label: "Cancel", intent: "cancel" }]);
        },

        cancel() {
            state.flow = null;
            save();
            return say(p("No problem. What else would you like to know?"), MAIN);
        },
    };

    /* ---------- understanding the visitor ---------- */

    const INTENTS = [
        ["thanks", /\b(thanks|thank you|thx|shukriya|shukria|jazak)/],
        ["greet", /^(hi+|hello|hey|salam|assalam|aoa|hlo|helo|good (morning|evening|afternoon))\b/],
        ["lead", /(quote|leave (my )?details|call me|contact me|hire you|hire|start (a )?project|get started)/],
        ["contact", /(whats ?app|number|phone|call|email|e-mail|contact|reach|talk to|baat)/],
        ["payment", /(jazz ?cash|easy ?paisa|payment|stripe|card payment|checkout)/],
        ["seo", /\b(seo|google|ranking|search engine)/],
        ["hosting", /(hosting|host|domain|server|live kar)/],
        ["urdu", /(urdu|language|multi.?lang|bilingual)/],
        ["admin", /(admin|cms|update.*(myself|khud)|khud.*(update|change)|edit (it|content))/],
        ["support", /(support|maintenance|after (the )?launch|baad me|help after|bug)/],
        ["mobile", /(mobile|responsive|phone friendly|tablet)/],
        ["timeline", /(how long|timeline|time lag|kitne din|kitna time|kitna waqt|kab tak|deadline|deliver|days|weeks)/],
        ["price", /(price|cost|rate|charge|budget|kitne|kitna|qeemat|keemat|paise|paisa|fee|rupees|\brs\b|afford|cheap|sasta)/],
        ["features", /(feature|extra|add.?on)/],
        ["process", /(process|steps|how do you work|kaise kaam|workflow)/],
        ["projects", /(project|portfolio|your work|samples?|examples?|kaam dikha|previous work|clients?)/],
        ["tech", /(tech|stack|django|python|react|javascript|framework|three\.?js)/],
        ["services", /(service|what do you (do|offer|make)|kya karte|kya banate|offer)/],
        ["location", /(where are you|location|based|city|faisalabad|pakistan)/],
        ["cv", /\b(cv|resume)\b/],
    ];

    function detect(text) {
        const t = text.toLowerCase();
        // "how much is an online store" -> price for that type
        const type = typeFromText(t);
        if (type && /(price|cost|kitne|kitna|qeemat|keemat|rate|budget|much)/.test(t)) return "type:" + type;
        for (const [name, re] of INTENTS) if (re.test(t)) return name;
        if (type) return "type:" + type;
        return "fallback";
    }

    /* ---------- lead flow ---------- */

    async function continueLead(text) {
        if (/^(cancel|stop|nahi|no thanks)$/i.test(text.trim())) return answers.cancel();

        if (state.flow === "lead_name") {
            state.lead.name = text.trim().slice(0, 100);
            state.flow = "lead_email";
            save();
            return say(p(`Nice to meet you, ${state.lead.name}! What's your email address?`), [{ label: "Cancel", intent: "cancel" }]);
        }

        if (state.flow === "lead_email") {
            const email = text.trim();
            if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email)) {
                return say(p("That doesn't look like an email address. Could you check it?"), [{ label: "Cancel", intent: "cancel" }]);
            }
            state.lead.email = email;
            state.flow = "lead_message";
            save();
            return say(p("Thanks! In a sentence or two, what would you like to build?"),
                [{ label: "Skip", intent: "skip" }, { label: "Cancel", intent: "cancel" }]);
        }

        if (state.flow === "lead_message") {
            state.lead.message = text === "__skip__" ? "" : text.trim();
            return submitLead();
        }
    }

    async function submitLead() {
        const t = typing();
        let ok = false, msg = "";
        try {
            const token = form.querySelector("[name=csrfmiddlewaretoken]").value;
            const res = await fetch(root.dataset.leadUrl, {
                method: "POST",
                headers: { "Content-Type": "application/json", "X-CSRFToken": token },
                body: JSON.stringify({ ...state.lead, website: form.querySelector(".cb-hp").value }),
            });
            const data = await res.json().catch(() => ({}));
            ok = res.ok && data.ok;
            if (!ok && data.errors) msg = Object.values(data.errors).flat()[0] || "";
        } catch (e) {
            msg = "";
        }
        t.remove();

        state.flow = null;
        if (ok) {
            const name = state.lead.name;
            state.lead = {};
            save();
            const box = el("div");
            box.append(
                p(`✅ Got it, ${name}! Rana will reply to your email, usually within 24 hours.`),
                p("Want a faster answer? Message him on WhatsApp:"),
                link("Chat on WhatsApp", waLink(`Hi Rana, I'm ${name}. I just left my details in your website chat.`), "cb-btn cb-btn-wa", true),
            );
            addBubble("bot", box);
            setChips([{ label: "🗂️ See projects", intent: "projects" }, { label: "💰 Prices", intent: "price" }]);
        } else {
            save();
            const box = el("div");
            box.append(
                p(msg || "Sorry, I couldn't send that just now."),
                p("You can still reach Rana directly:"),
                link("Chat on WhatsApp", waLink(), "cb-btn cb-btn-wa", true),
            );
            addBubble("bot", box);
            setChips(MAIN);
        }
    }

    /* ---------- main handler ---------- */

    async function handleUser(text, intent) {
        if (busy) return;
        busy = true;
        quick.replaceChildren();

        try {
            await getKnowledge();
        } catch (e) {
            addBubble("bot", "Sorry, I can't load my answers right now. Please message Rana on WhatsApp.");
            busy = false;
            return;
        }

        if (intent === "skip") {
            addBubble("user", "Skip");
            await continueLead("__skip__");
            busy = false;
            return;
        }

        if (text) addBubble("user", text);

        if (state.flow && !intent) {
            await continueLead(text);
        } else {
            if (intent && intent !== "cancel") state.flow = null;
            const key = intent || detect(text);
            if (key.startsWith("type:")) await priceFor(key.slice(5));
            else await (answers[key] || answers.fallback)();
        }
        busy = false;
        input.focus({ preventScroll: true });
    }

    /* ---------- open / close ---------- */

    function hideTeaser() {
        teaser.classList.remove("is-open");
        setTimeout(() => { teaser.hidden = true; }, 300);
        badge.hidden = true;
        try { sessionStorage.setItem("cb-teased", "1"); } catch (e) {}
    }

    async function open() {
        hideTeaser();
        panel.hidden = false;
        requestAnimationFrame(() => panel.classList.add("is-open"));
        launcher.setAttribute("aria-expanded", "true");
        launcher.setAttribute("aria-label", "Close chat assistant");
        html.classList.add("cb-open");
        try { sessionStorage.setItem("cb-was-open", "1"); } catch (e) {}

        if (!state.log.length) {
            busy = true;
            try {
                await getKnowledge();
                await say([
                    p("Hi! 👋 I'm Rana's website assistant."),
                    p("I can tell you about prices, timelines, services and past projects, or pass your details to Rana."),
                ], MAIN);
            } catch (e) {
                addBubble("bot", "Hi! I can't load my answers right now, but you can message Rana on WhatsApp.", false);
            }
            busy = false;
        }
        if (window.matchMedia("(pointer: fine)").matches) input.focus({ preventScroll: true });
    }

    function close() {
        panel.classList.remove("is-open");
        launcher.setAttribute("aria-expanded", "false");
        launcher.setAttribute("aria-label", "Open chat assistant");
        html.classList.remove("cb-open");
        setTimeout(() => { if (!panel.classList.contains("is-open")) panel.hidden = true; }, reduceMotion ? 0 : 300);
        try { sessionStorage.removeItem("cb-was-open"); } catch (e) {}
    }

    launcher.addEventListener("click", () => (panel.hidden ? open() : close()));
    $("cbClose").addEventListener("click", () => { close(); launcher.focus(); });
    $("cbTeaserOpen").addEventListener("click", open);
    $("cbTeaserClose").addEventListener("click", hideTeaser);

    $("cbRestart").addEventListener("click", () => {
        if (busy) return;
        state = { log: [], flow: null, lead: {}, chips: null };
        save();
        body.replaceChildren();
        quick.replaceChildren();
        open();
    });

    form.addEventListener("submit", (e) => {
        e.preventDefault();
        const text = input.value.trim();
        if (!text || busy) return;
        input.value = "";
        handleUser(text);
    });

    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape" && !panel.hidden) { close(); launcher.focus(); }
    });

    /* ---------- start ---------- */

    if (state.log.length) restoreLog();

    let wasOpen = false, teased = false;
    try {
        wasOpen = !!sessionStorage.getItem("cb-was-open");
        teased = !!sessionStorage.getItem("cb-teased");
    } catch (e) {}

    // Deep links: /?chat=1 opens the assistant, /?chat=1&ask=price asks a question.
    const params = new URLSearchParams(location.search);

    if (params.get("chat")) {
        open().then(() => {
            const question = (params.get("ask") || "").trim().slice(0, 200);
            if (question) handleUser(question);
        });
    } else if (wasOpen) {
        open();
    } else if (!teased) {
        // Say hello once per visit, a few seconds in.
        setTimeout(() => {
            if (!panel.hidden || html.classList.contains("sn-open")) return;
            if (document.activeElement?.matches("input, textarea, select")) return;
            teaser.hidden = false;
            badge.hidden = false;
            requestAnimationFrame(() => teaser.classList.add("is-open"));
            try { sessionStorage.setItem("cb-teased", "1"); } catch (e) {}
        }, 7000);
    }

})();
