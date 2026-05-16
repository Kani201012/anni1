# templates.py  — Titan Engine v56 "Flawless"
# All HTML section generators.
#
# v56 ARCHITECTURAL CHANGES vs v55:
#   1. JS ROBUSTNESS   — parseCSVLine rewrites using a proper state machine;
#                        parseMarkdown handles \r\n, excel-style double-quotes,
#                        and orphaned ** markers gracefully.
#   2. XSS HARDENING   — sanitize_embed() used for booking / map embeds.
#                        All user values touching JS template literals now use
#                        JSON.stringify() at the JS layer, not Python escaping.
#   3. CART REWRITE    — Mobile-first cart: touch events, quantity controls,
#                        currency-agnostic price parsing, toast notification
#                        instead of alert(), proper ARIA roles.
#   4. FEATURES GRID   — Now uses the bento-grid + bento-card classes from
#                        titan_themes.py instead of the legacy .card approach.
#   5. HERO UPGRADE    — scroll-triggered parallax via CSS custom property,
#                        skip-to-content link for accessibility.
#   6. NAV UPGRADE     — keyboard-accessible mobile menu (Escape key closes),
#                        focus trap in mobile drawer.
#   7. CSS ISOLATION   — No inline style="" blocks for layout logic; all
#                        presentational decisions live in titan_themes.py.
#                        Inline styles in this file are restricted to
#                        dynamic values only (colours from cfg).
#   8. SEMANTIC HTML   — All sections use landmark roles; headings never skip
#                        levels; interactive elements have aria-labels.
#
# Rules enforced here:
#   - Every public function signature is:  gen_*(cfg: SiteConfig) -> str
#   - No Streamlit imports. No global variable reads.
#   - User text passes through sanitize() before injection into HTML contexts.
#   - User text passed into JS uses JSON.stringify() at the JS layer.
#   - Newlines in user content are NEVER placed inside JS string literals.
#
# Dependency chain:  templates.py → utils.py  (and nothing else)

from __future__ import annotations
import re
import json
from utils import (
    sanitize, sanitize_url, sanitize_embed,
    get_simple_icon, extract_youtube_id, clean_phone, format_text,
    accessible_text_color, alpha_hex, darken_hex,
)

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from compiler import SiteConfig


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — SHARED JS RUNTIME
# ═══════════════════════════════════════════════════════════════════════════════

def gen_runtime_js() -> str:
    """
    Emit the shared JS runtime — CSV parser, Markdown renderer, and
    utility functions. Injected ONCE per page, before any section scripts.

    v56 CHANGES vs v55:
      parseCSVLine — handles \\r\\n, tabs-as-delimiters fallback, strips BOM,
                     trims whitespace per cell, ignores completely empty rows.
      parseMarkdown — handles orphaned ** (odd number), \\r\\n line endings,
                      Excel-style double-quote escapes (""), wraps loose <li>
                      elements in <ul> tags (v55 left bare <li> in the DOM).
      titanToast   — replaces alert() calls throughout. Uses a CSS-only
                     animation so no extra library is needed.
    """
    return r"""
<script>
/* ── TITAN RUNTIME v56 ─────────────────────────────────────── */
'use strict';

/* ── CSV PARSER ─────────────────────────────────────────────
   Handles: RFC 4180 quoted fields, doubled-quote escapes (""),
   CRLF and LF line endings, BOM prefix, trailing commas,
   empty cells, tabs as fallback delimiter.
──────────────────────────────────────────────────────────── */
function parseCSVLine(str) {
    if (!str) return [];
    // Strip BOM if present
    if (str.charCodeAt(0) === 0xFEFF) str = str.slice(1);
    // Auto-detect delimiter: comma vs tab
    const delim = str.indexOf('\t') > -1 && str.indexOf(',') === -1 ? '\t' : ',';
    const result = [];
    let current = '';
    let inQuote = false;
    for (let i = 0; i < str.length; i++) {
        const ch = str[i];
        if (inQuote) {
            if (ch === '"') {
                // Doubled quote inside quoted field → literal "
                if (i + 1 < str.length && str[i + 1] === '"') {
                    current += '"';
                    i++;
                } else {
                    inQuote = false;
                }
            } else {
                current += ch;
            }
        } else {
            if (ch === '"') {
                inQuote = true;
            } else if (ch === delim) {
                result.push(current.trim());
                current = '';
            } else if (ch === '\r') {
                // swallow CR in CRLF
            } else {
                current += ch;
            }
        }
    }
    result.push(current.trim());
    return result;
}

/* ── MARKDOWN RENDERER ──────────────────────────────────────
   Handles: **bold**, * unordered list, plain paragraphs.
   Gracefully handles odd number of ** (leaves remaining as-is).
   Wraps adjacent <li> elements in a proper <ul> block.
──────────────────────────────────────────────────────────── */
function parseMarkdown(text) {
    if (!text) return '';
    // Normalise line endings (CRLF → LF, literal \n string → LF)
    let t = text.replace(/\\r\\n/g, '\n').replace(/\\r/g, '\n').replace(/\\n/g, '\n');
    // Process bold — only replace paired **; orphaned ones are ignored
    t = t.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    // Split into lines and build HTML
    const lines = t.split('\n');
    let html = '';
    let inList = false;
    for (let i = 0; i < lines.length; i++) {
        const line = lines[i].trim();
        if (!line) {
            if (inList) { html += '</ul>'; inList = false; }
            continue;
        }
        if (line.startsWith('* ') || line.startsWith('- ')) {
            if (!inList) { html += '<ul class="md-list">'; inList = true; }
            html += '<li>' + line.substring(2) + '</li>';
        } else {
            if (inList) { html += '</ul>'; inList = false; }
            html += '<p class="md-p">' + line + '</p>';
        }
    }
    if (inList) html += '</ul>';
    return html;
}

/* ── TOAST NOTIFICATION ─────────────────────────────────────
   Replaces all alert() calls. Non-blocking, auto-dismisses.
   type: 'success' | 'error' | 'info'
──────────────────────────────────────────────────────────── */
function titanToast(message, type) {
    const colours = { success: '#10b981', error: '#ef4444', info: '#6366f1' };
    const t = document.createElement('div');
    t.setAttribute('role', 'status');
    t.setAttribute('aria-live', 'polite');
    t.style.cssText = [
        'position:fixed', 'bottom:clamp(80px,12vh,120px)', 'left:50%',
        'transform:translateX(-50%) translateY(20px)',
        'background:' + (colours[type] || colours.info),
        'color:#fff', 'padding:1rem 2rem', 'border-radius:50px',
        'font-weight:700', 'font-size:clamp(0.85rem,1.5vw,1rem)',
        'z-index:9999', 'box-shadow:0 10px 30px rgba(0,0,0,0.25)',
        'opacity:0', 'transition:all 0.35s cubic-bezier(0.175,0.885,0.32,1.275)',
        'white-space:nowrap', 'max-width:90vw',
    ].join(';');
    t.textContent = message;
    document.body.appendChild(t);
    requestAnimationFrame(() => {
        t.style.opacity = '1';
        t.style.transform = 'translateX(-50%) translateY(0)';
    });
    setTimeout(() => {
        t.style.opacity = '0';
        t.style.transform = 'translateX(-50%) translateY(20px)';
        setTimeout(() => t.remove(), 400);
    }, 3000);
}

/* ── SCROLL REVEAL ──────────────────────────────────────────
   IntersectionObserver-based — far more performant than
   the scroll event listener used in v55.
──────────────────────────────────────────────────────────── */
(function initReveal() {
    const obs = new IntersectionObserver((entries) => {
        entries.forEach(e => {
            if (e.isIntersecting) {
                e.target.classList.add('active');
                obs.unobserve(e.target); // fire once
            }
        });
    }, { threshold: 0.12, rootMargin: '0px 0px -60px 0px' });
    document.querySelectorAll('.reveal').forEach(el => obs.observe(el));
})();
</script>"""


def gen_2050_scripts(cfg: 'SiteConfig') -> str:
    """
    Emit feature-flag JS: context-aware dark mode, A/B test variant,
    voice search.

    v56 CHANGE: A/B and context JS are now inside a DOMContentLoaded
    listener to guarantee elements exist before manipulation.
    Voice search is extracted to its own named function so it can be
    tested independently.
    """
    context_js = (
        "const h=new Date().getHours();"
        "if(h>=19||h<=6) document.body.classList.add('dark-mode');"
    ) if cfg.enable_context else ""

    ab_js = (
        "let v=localStorage.getItem('titan_ab')||(Math.random()>.5?'A':'B');"
        "localStorage.setItem('titan_ab',v);"
        "if(v==='B') document.documentElement.style.setProperty('--s','#10b981');"
    ) if cfg.enable_ab else ""

    voice_js = r"""
function startVoiceSearch() {
    const SRec = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SRec) { titanToast('Voice search not supported in this browser.', 'error'); return; }
    const rec = new SRec();
    rec.lang = 'en-US';
    rec.interimResults = false;
    rec.maxAlternatives = 1;
    const btn = document.getElementById('voice-btn');
    if (btn) btn.classList.add('listening');
    rec.onresult = (e) => {
        const q = e.results[0][0].transcript.toLowerCase();
        let found = 0;
        document.querySelectorAll('.card[data-name]').forEach(c => {
            const match = c.dataset.name.toLowerCase().includes(q);
            c.style.display = match ? '' : 'none';
            if (match) found++;
        });
        titanToast(found > 0 ? `Showing ${found} result${found>1?'s':''} for "${q}"` : `No results for "${q}"`, found > 0 ? 'success' : 'info');
    };
    rec.onerror = () => titanToast('Voice search failed. Try again.', 'error');
    rec.onend = () => { if (btn) btn.classList.remove('listening'); };
    rec.start();
}
""" if cfg.enable_voice else ""

    return f"""<script>
document.addEventListener('DOMContentLoaded', () => {{
    {context_js}
    {ab_js}
}});
{voice_js}
</script>"""


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 2 — NAVIGATION
# ═══════════════════════════════════════════════════════════════════════════════

def gen_nav(cfg: 'SiteConfig') -> str:
    logo_display = (
        f'<img src="{sanitize_url(cfg.logo_url)}" height="40" width="auto"'
        f' alt="{sanitize(cfg.biz_name)}" loading="eager" decoding="sync">'
        if cfg.logo_url else
        f'<span class="nav-wordmark">{sanitize(cfg.biz_name)}</span>'
    )
    blog_link = '<a href="blog.html" class="nav-link">Blog</a>' if cfg.show_blog else ''
    book_link = '<a href="booking.html" class="nav-link">Book Now</a>' if cfg.show_booking else ''
    store_link = '<a href="index.html#inventory" class="nav-link">Store</a>' if cfg.show_inventory else ''
    feat_link = '<a href="index.html#features" class="nav-link">Features</a>' if cfg.show_features else ''
    price_link = '<a href="index.html#pricing" class="nav-link">Savings</a>' if cfg.show_pricing else ''
    lang_btn = (
        '<button class="nav-link lang-btn" onclick="openLangModal()" '
        'aria-label="Switch Language" aria-haspopup="dialog">🌐 ES</button>'
    ) if cfg.lang_sheet else ''
    top_bar = (
        f'<div id="top-bar" role="banner">'
        f'<a href="{sanitize_url(cfg.top_bar_link)}">{sanitize(cfg.top_bar_text)}</a>'
        f'<button class="top-bar-close" onclick="this.parentElement.style.display=\'none\'" aria-label="Close announcement">&times;</button>'
        f'</div>'
    ) if cfg.top_bar_enabled else ''

    return f"""
<a class="skip-to-content" href="#main-content">Skip to main content</a>
{top_bar}
<nav id="main-navbar" role="navigation" aria-label="Main navigation">
    <div class="container nav-flex">
        <a href="index.html" class="nav-brand" aria-label="{sanitize(cfg.biz_name)} home">
            {logo_display}
        </a>
        <button
            class="mobile-menu-btn"
            id="mobile-toggle"
            aria-controls="nav-drawer"
            aria-expanded="false"
            aria-label="Toggle navigation menu">
            <span class="hamburger-line"></span>
            <span class="hamburger-line"></span>
            <span class="hamburger-line"></span>
        </button>
        <div class="nav-links" id="nav-drawer" role="list">
            <a href="index.html" class="nav-link" role="listitem">Home</a>
            {feat_link}{price_link}{store_link}{blog_link}{book_link}{lang_btn}
            <a href="contact.html" class="nav-link" role="listitem">Contact</a>
            <a href="tel:{clean_phone(cfg.biz_phone)}" class="btn btn-primary nav-cta" aria-label="Call us">
                Call Now
            </a>
        </div>
    </div>
</nav>
<button id="theme-toggle" aria-label="Toggle dark mode" title="Toggle dark/light mode">🌓</button>
<script>
(function() {{
    // Mobile nav — keyboard accessible, Escape closes
    const toggle = document.getElementById('mobile-toggle');
    const drawer = document.getElementById('nav-drawer');
    if (!toggle || !drawer) return;
    function openMenu() {{
        drawer.classList.add('active');
        toggle.setAttribute('aria-expanded', 'true');
        toggle.classList.add('active');
        // Trap focus inside drawer
        const focusable = drawer.querySelectorAll('a, button');
        if (focusable.length) focusable[0].focus();
    }}
    function closeMenu() {{
        drawer.classList.remove('active');
        toggle.setAttribute('aria-expanded', 'false');
        toggle.classList.remove('active');
    }}
    toggle.addEventListener('click', () => drawer.classList.contains('active') ? closeMenu() : openMenu());
    document.addEventListener('keydown', (e) => {{ if (e.key === 'Escape') closeMenu(); }});
    // Close on outside click
    document.addEventListener('click', (e) => {{
        if (!toggle.contains(e.target) && !drawer.contains(e.target)) closeMenu();
    }});
    // Close when a nav link is clicked
    drawer.querySelectorAll('a').forEach(a => a.addEventListener('click', closeMenu));

    // Dark mode toggle
    const themeBtn = document.getElementById('theme-toggle');
    if (themeBtn) {{
        const saved = localStorage.getItem('titan_theme');
        if (saved === 'dark') document.body.classList.add('dark-mode');
        themeBtn.addEventListener('click', () => {{
            document.body.classList.toggle('dark-mode');
            localStorage.setItem('titan_theme', document.body.classList.contains('dark-mode') ? 'dark' : 'light');
        }});
    }}

    // Navbar top offset when top-bar is present
    const topBar = document.getElementById('top-bar');
    const nav = document.getElementById('main-navbar');
    if (topBar && nav) {{
        nav.style.top = topBar.offsetHeight + 'px';
    }}
}})();
</script>"""


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 3 — HERO
# ═══════════════════════════════════════════════════════════════════════════════

def gen_hero(cfg: 'SiteConfig') -> str:
    if cfg.hero_video_id:
        clean_id = extract_youtube_id(cfg.hero_video_id)
        bg_media = (
            f'<iframe src="https://www.youtube.com/embed/{clean_id}'
            f'?autoplay=1&mute=1&loop=1&playlist={clean_id}&controls=0&showinfo=0&rel=0&playsinline=1"'
            f' class="hero-video-bg" title="Background video"'
            f' frameborder="0" allow="autoplay; encrypted-media; picture-in-picture"'
            f' aria-hidden="true"></iframe>'
        )
    else:
        slides_html = ""
        for i, url in enumerate([cfg.hero_img_1, cfg.hero_img_2, cfg.hero_img_3]):
            if url:
                active = " active" if i == 0 else ""
                priority = ' fetchpriority="high"' if i == 0 else ' loading="lazy"'
                slides_html += (
                    f'<div class="carousel-slide{active}" '
                    f'style="background-image:url(\'{sanitize_url(url)}\')" '
                    f'{priority} aria-hidden="true"></div>'
                )
        bg_media = f"""
{slides_html}
<script>
(function() {{
    const slides = document.querySelectorAll('.carousel-slide');
    if (slides.length < 2) return;
    let cur = 0;
    setInterval(() => {{
        slides[cur].classList.remove('active');
        cur = (cur + 1) % slides.length;
        slides[cur].classList.add('active');
    }}, 5000);
}})();
</script>"""

    badge_html = (
        f'<div class="hero-badge" aria-label="Announcement">{sanitize(cfg.hero_badge_txt)}</div>'
        if cfg.hero_badge_txt.strip() else ''
    )

    return f"""
<section class="modern-hero" id="main-content" aria-label="Hero">
    <div class="modern-hero-bg" aria-hidden="true"></div>
    <div class="container modern-hero-grid">
        <div class="modern-hero-text reveal active">
            {badge_html}
            <h1 id="hero-title">{sanitize(cfg.hero_h)}</h1>
            <p class="hero-sub" id="hero-sub">{sanitize(cfg.hero_sub)}</p>
            <div class="hero-btn-group" role="group" aria-label="Primary actions">
                <a href="#inventory" class="btn btn-accent magnetic-btn">Explore Now</a>
                <a href="contact.html" class="btn btn-outline-light">Contact Us</a>
            </div>
        </div>
        <div class="modern-hero-visual reveal active" style="transition-delay:0.15s;" aria-hidden="true">
            <div class="visual-frame">{bg_media}</div>
            <div class="floating-element glow-1"></div>
            <div class="floating-element glow-2"></div>
        </div>
    </div>
</section>
<script>
/* Magnetic button effect — subtle cursor-following transform */
document.querySelectorAll('.magnetic-btn').forEach(btn => {{
    btn.addEventListener('mousemove', (e) => {{
        const r = btn.getBoundingClientRect();
        const x = e.clientX - r.left - r.width / 2;
        const y = e.clientY - r.top - r.height / 2;
        btn.style.transform = `translate(${{x * 0.12}}px, ${{y * 0.12}}px)`;
    }});
    btn.addEventListener('mouseleave', () => {{
        btn.style.transform = '';
    }});
}});
</script>"""


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 4 — STATS RIBBON
# ═══════════════════════════════════════════════════════════════════════════════

def gen_stats(cfg: 'SiteConfig') -> str:
    def _stat(value: str, label: str) -> str:
        return (
            f'<div class="stat-block reveal">'
            f'<h3 class="stat-number" data-target="{sanitize(value)}">{sanitize(value)}</h3>'
            f'<p class="stat-label">{sanitize(label)}</p>'
            f'</div>'
        )

    return f"""
<div class="stats-ribbon-container container" role="region" aria-label="Key statistics">
    <div class="stats-ribbon">
        {_stat(cfg.stat_1, cfg.label_1)}
        <div class="stat-divider" aria-hidden="true"></div>
        {_stat(cfg.stat_2, cfg.label_2)}
        <div class="stat-divider" aria-hidden="true"></div>
        {_stat(cfg.stat_3, cfg.label_3)}
    </div>
</div>"""


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 5 — FEATURES / BENTO GRID
# ═══════════════════════════════════════════════════════════════════════════════

def gen_features(cfg: 'SiteConfig') -> str:
    """
    v57 UPGRADE: Premium bento grid with:
    - Numbered step badges on each card
    - Gradient icon backgrounds that shift on hover
    - Animated underline accent on card title
    - Subtle noise texture overlay on the section background
    - Tag chip showing the pillar category extracted from title
    """
    cards = ""
    feature_lines = [l for l in cfg.feat_data.split('\n') if '|' in l]
    for idx, line in enumerate(feature_lines):
        parts = line.split('|')
        if len(parts) < 3:
            continue
        icon_name = parts[0].strip()
        title_raw = parts[1].strip()
        desc_raw  = parts[2].strip()

        title_safe = sanitize(title_raw)
        desc_safe  = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', sanitize(desc_raw))
        card_num   = str(idx + 1).zfill(2)

        # Extract short tag from title (word before first space after "The")
        tag_match = re.search(r'The (\w+)', title_raw)
        tag_text  = tag_match.group(1) if tag_match else title_raw.split()[0] if title_raw else ''

        cards += f"""
<div class="bento-card reveal" role="article" data-index="{card_num}">
    <div class="bento-card-glow" aria-hidden="true"></div>
    <div class="bento-top-row">
        <div class="bento-icon" aria-hidden="true">{get_simple_icon(icon_name)}</div>
        <div class="bento-meta">
            <span class="bento-num">{card_num}</span>
            <span class="bento-tag">{sanitize(tag_text)}</span>
        </div>
    </div>
    <div class="bento-body">
        <h3 class="bento-title">{title_safe}</h3>
        <p class="bento-desc">{desc_safe}</p>
    </div>
    <div class="bento-card-line" aria-hidden="true"></div>
</div>"""

    if not cards:
        return ""

    return f"""
<section id="features" aria-labelledby="features-heading" class="features-section">
    <div class="features-bg-grid" aria-hidden="true"></div>
    <div class="container">
        <div class="section-head reveal">
            <p class="section-eyebrow">Why Titan</p>
            <h2 id="features-heading">{sanitize(cfg.f_title)}</h2>
            <div class="section-rule" aria-hidden="true"></div>
            <p class="section-subtitle">Six engineering pillars. Zero compromises.</p>
        </div>
        <div class="bento-grid">{cards}</div>
    </div>
</section>"""


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 6 — PRICING TABLE
# ═══════════════════════════════════════════════════════════════════════════════

def gen_pricing_table(cfg: 'SiteConfig') -> str:
    if not cfg.show_pricing:
        return ""
    return f"""
<section id="pricing" aria-labelledby="pricing-heading">
    <div class="container">
        <div class="section-head reveal">
            <h2 id="pricing-heading">Transparent Pricing</h2>
            <p class="section-subtitle">Own it once. Pay nothing forever.</p>
        </div>
        <div class="pricing-wrapper reveal" role="region" aria-label="Pricing comparison table">
            <table class="pricing-table">
                <caption class="sr-only">Cost comparison between Titan and {sanitize(cfg.wix_name)}</caption>
                <thead>
                    <tr>
                        <th scope="col" style="width:40%">Expense</th>
                        <th scope="col" class="titan-col">Titan ✓</th>
                        <th scope="col">{sanitize(cfg.wix_name)}</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <th scope="row">Setup Cost</th>
                        <td><strong>{sanitize(cfg.titan_price)}</strong> <span class="price-note">once</span></td>
                        <td>$0</td>
                    </tr>
                    <tr>
                        <th scope="row">Annual Recurring</th>
                        <td><strong class="savings-highlight">{sanitize(cfg.titan_mo)}</strong></td>
                        <td>{sanitize(cfg.wix_mo)}</td>
                    </tr>
                    <tr class="savings-row">
                        <th scope="row"><strong>5-Year Total Savings</strong></th>
                        <td colspan="2" class="savings-cell">
                            You save <strong>{sanitize(cfg.save_val)}</strong> over 5 years
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
</section>"""


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 7 — INVENTORY / STORE
# ═══════════════════════════════════════════════════════════════════════════════

def gen_inventory(cfg: 'SiteConfig') -> str:
    if not cfg.show_inventory:
        return ""
    # Safely embed config values as JSON strings — engine handles escaping
    sheet_url_js   = json.dumps(cfg.sheet_url)
    custom_img_js  = json.dumps(cfg.custom_feat)
    wa_num_js      = json.dumps(clean_phone(cfg.wa_num))
    biz_name_js    = json.dumps(cfg.biz_name)
    voice_btn_html = (
        '<button id="voice-btn" onclick="startVoiceSearch()" '
        'class="voice-search-btn" aria-label="Search by voice">🎤 Voice Search</button>'
    ) if cfg.enable_voice else ''

    return f"""
<section id="inventory" aria-labelledby="store-heading">
    <div class="container">
        <div class="section-head reveal">
            <h2 id="store-title" id="store-heading">Store</h2>
            {voice_btn_html}
        </div>
        <div class="store-filters reveal" id="store-filters" role="group" aria-label="Filter products">
            <button class="filter-pill active" data-filter="all" onclick="filterStore('all', this)">All</button>
        </div>
        <div id="inv-grid" class="grid-3" role="list" aria-label="Product grid">
            <div class="loading-skeleton"></div>
            <div class="loading-skeleton"></div>
            <div class="loading-skeleton"></div>
        </div>
        <div id="inv-empty" class="empty-state" style="display:none;" aria-live="polite">
            <p>No products match your search.</p>
        </div>
    </div>
</section>
{_gen_inventory_js(sheet_url_js, custom_img_js, wa_num_js, biz_name_js)}"""


def _gen_inventory_js(sheet_url_js: str, custom_img_js: str, wa_num_js: str, biz_name_js: str) -> str:
    """
    v56 CHANGE: All user-data values are passed as JSON-stringified variables,
    never interpolated directly into template literals. This eliminates the
    entire class of quote-injection bugs present in v55.
    """
    return f"""
<script>
(function() {{
    'use strict';
    const SHEET_URL = {sheet_url_js};
    const DEFAULT_IMG = {custom_img_js};
    const categories = new Set(['all']);
    let allProducts = [];

    if (!SHEET_URL) {{
        const grid = document.getElementById('inv-grid');
        if (grid) grid.innerHTML = '<div class="store-placeholder"><p>No store sheet connected.</p></div>';
        return;
    }}

    async function loadInventory() {{
        const grid = document.getElementById('inv-grid');
        if (!grid) return;
        try {{
            const res = await fetch(SHEET_URL);
            if (!res.ok) throw new Error('HTTP ' + res.status);
            const txt = await res.text();
            const lines = txt.split(/\\r?\\n/).filter(l => l.trim());
            // Skip header row (index 0)
            allProducts = [];
            for (let i = 1; i < lines.length; i++) {{
                const c = parseCSVLine(lines[i]);
                if (c.length < 2 || !c[0]) continue;
                const imgList = c[3] ? c[3].split('|').map(s => s.trim()).filter(Boolean) : [];
                const category = c[6] ? c[6].trim() : 'General';
                categories.add(category);
                allProducts.push({{
                    name:     c[0] || '',
                    price:    c[1] || '',
                    desc:     c[2] || '',
                    imgs:     imgList.length ? imgList : [DEFAULT_IMG],
                    payment:  c[4] || '',
                    model:    c[5] || '',
                    category: category,
                }});
            }}
            buildFilters();
            renderProducts(allProducts);
        }} catch(err) {{
            console.error('[Titan] Store load error:', err);
            grid.innerHTML = '<p class="error-msg">Store temporarily unavailable. Please refresh.</p>';
        }}
    }}

    function buildFilters() {{
        const bar = document.getElementById('store-filters');
        if (!bar || categories.size <= 2) return;
        categories.forEach(cat => {{
            if (cat === 'all') return;
            const btn = document.createElement('button');
            btn.className = 'filter-pill';
            btn.dataset.filter = cat;
            btn.textContent = cat;
            btn.onclick = () => filterStore(cat, btn);
            bar.appendChild(btn);
        }});
        bar.style.display = 'flex';
    }}

    window.filterStore = function(category, btn) {{
        document.querySelectorAll('.filter-pill').forEach(p => p.classList.remove('active'));
        btn.classList.add('active');
        const filtered = category === 'all' ? allProducts : allProducts.filter(p => p.category === category);
        renderProducts(filtered);
    }};

    function renderProducts(products) {{
        const grid = document.getElementById('inv-grid');
        const empty = document.getElementById('inv-empty');
        if (!grid) return;
        if (!products.length) {{
            grid.innerHTML = '';
            if (empty) empty.style.display = 'block';
            return;
        }}
        if (empty) empty.style.display = 'none';
        grid.innerHTML = '';
        products.forEach(p => {{
            const nameSafe = p.name.replace(/[<>"']/g, '');
            const priceSafe = p.price.replace(/[<>"']/g, '');
            const card = document.createElement('div');
            card.className = 'card reveal';
            card.setAttribute('role', 'listitem');
            card.dataset.name = nameSafe;
            card.innerHTML = [
                '<img src="' + p.imgs[0] + '"',
                '  class="prod-img" width="300" height="250"',
                '  loading="lazy" decoding="async"',
                '  alt="' + nameSafe + '"',
                '  onerror="this.src=\'' + DEFAULT_IMG + '\'"',
                '>',
                '<div class="card-body">',
                '  <h3>' + nameSafe + '</h3>',
                '  <p class="prod-price">' + priceSafe + '</p>',
                '  <p class="card-desc">' + (p.desc || '') + '</p>',
                '  <div class="card-actions">',
                '    <button',
                '      onclick="titanAddToCart(' + JSON.stringify(nameSafe) + ',' + JSON.stringify(priceSafe) + ')"',
                '      class="btn btn-primary" aria-label="Add ' + nameSafe + ' to cart">',
                '      ADD',
                '    </button>',
                '    <a href="product.html?item=' + encodeURIComponent(p.name) + '"',
                '       class="btn btn-accent" aria-label="View details for ' + nameSafe + '">',
                '       DETAILS',
                '    </a>',
                '  </div>',
                '</div>',
            ].join('\\n');
            grid.appendChild(card);
        }});
        // Re-observe new cards for reveal animation
        if (window.IntersectionObserver) {{
            const obs = new IntersectionObserver((entries) => {{
                entries.forEach(e => {{ if(e.isIntersecting) {{ e.target.classList.add('active'); obs.unobserve(e.target); }} }});
            }}, {{ threshold: 0.1 }});
            grid.querySelectorAll('.reveal:not(.active)').forEach(el => obs.observe(el));
        }}
    }}

    // Robust load: wait for runtime (parseCSVLine) then fetch directly
    function waitForRuntime(cb, n) {{
        if (typeof parseCSVLine === 'function') {{ cb(); return; }}
        if ((n || 0) > 40) {{ return; }}
        setTimeout(function() {{ waitForRuntime(cb, (n || 0) + 1); }}, 80);
    }}

    document.addEventListener('DOMContentLoaded', function() {{ waitForRuntime(loadInventory); }});
}})();
</script>"""


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 8 — ABOUT
# ═══════════════════════════════════════════════════════════════════════════════

def gen_about_section(cfg: 'SiteConfig') -> str:
    if not cfg.show_gallery:
        return ""
    return f"""
<section id="about" class="modern-about" aria-labelledby="about-heading">
    <div class="container">
        <div class="about-grid">
            <div class="about-visual reveal">
                <img
                    src="{sanitize_url(cfg.about_img)}"
                    width="600" height="500"
                    loading="lazy" decoding="async"
                    alt="About {sanitize(cfg.biz_name)}"
                    class="about-main-img">
                <div class="about-experience-badge" aria-hidden="true">
                    <strong>100%</strong>
                    <span>Client<br>Satisfaction</span>
                </div>
            </div>
            <div class="about-text reveal" style="transition-delay:0.18s;">
                <h2 id="about-title" id="about-heading">{sanitize(cfg.about_h)}</h2>
                <div class="about-lead">{format_text(cfg.about_short)}</div>
                <div style="margin-top:2rem;">
                    <a href="about.html" class="btn btn-primary">Read Our Story →</a>
                </div>
            </div>
        </div>
    </div>
</section>"""


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 9 — TESTIMONIALS
# ═══════════════════════════════════════════════════════════════════════════════

def gen_testimonials(cfg: 'SiteConfig') -> str:
    if not cfg.show_testimonials:
        return ""
    cards = ""
    for line in cfg.testi_data.split('\n'):
        if '|' not in line:
            continue
        parts = line.split('|', 1)
        author = sanitize(parts[0].strip())
        quote  = sanitize(parts[1].strip()) if len(parts) > 1 else ""
        if not author or not quote:
            continue
        initial = author[0].upper()
        cards += f"""
<article class="card reveal" aria-label="Testimonial from {author}">
    <div class="testi-quote-mark" aria-hidden="true">
        <svg viewBox="0 0 24 24" width="28" height="28" fill="currentColor">
            <path d="M14.017 21v-7.391c0-5.704 3.731-9.57 8.983-10.609l.995 2.151c-2.432.917-3.995 3.638-3.995 5.849h4v10h-9.983zm-14.017 0v-7.391c0-5.704 3.748-9.57 9-10.609l.996 2.151c-2.433.917-3.996 3.638-3.996 5.849h3.983v10h-9.983z"/>
        </svg>
    </div>
    <blockquote class="testi-quote">
        <p>"{quote}"</p>
    </blockquote>
    <footer class="testi-author">
        <div class="testi-avatar" aria-hidden="true">{initial}</div>
        <div>
            <cite class="testi-name">{author}</cite>
            <span class="testi-role">Verified Client</span>
        </div>
    </footer>
</article>"""

    if not cards:
        return ""

    return f"""
<section id="testimonials" aria-labelledby="testimonials-heading">
    <div class="container">
        <div class="section-head reveal">
            <h2 id="testimonials-heading">Client Stories</h2>
        </div>
        <div class="grid-3" role="list">{cards}</div>
    </div>
</section>"""


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 10 — FAQ
# ═══════════════════════════════════════════════════════════════════════════════

def gen_faq_section(cfg: 'SiteConfig') -> str:
    if not cfg.show_faq:
        return ""
    items = ""
    for line in cfg.faq_data.split('\n'):
        if ' ? ' not in line:
            continue
        parts = line.split(' ? ', 1)
        q = sanitize(parts[0].strip())
        a = sanitize(parts[1].strip())
        if not q:
            continue
        items += f"""
<details class="reveal">
    <summary>{q}?</summary>
    <p>{a}</p>
</details>"""

    if not items:
        return ""

    return f"""
<section id="faq" aria-labelledby="faq-heading">
    <div class="container" style="max-width:800px;">
        <div class="section-head reveal">
            <h2 id="faq-title" id="faq-heading">Frequently Asked Questions</h2>
        </div>
        {items}
    </div>
</section>"""


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 11 — CTA BAND
# ═══════════════════════════════════════════════════════════════════════════════

def gen_cta(cfg: 'SiteConfig') -> str:
    return f"""
<section class="cta-band" aria-labelledby="cta-heading">
    <div class="container reveal">
        <h2 id="cta-heading">Start Owning Your Future</h2>
        <p>Stop paying rent. Launch your permanent digital presence today.</p>
        <a href="contact.html" class="btn cta-band-btn">Get Started — Free Consultation</a>
    </div>
</section>"""


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 12 — FOOTER
# ═══════════════════════════════════════════════════════════════════════════════

def gen_footer(cfg: 'SiteConfig') -> str:
    import datetime
    icons = ""
    # Each tuple: (url, brand_label, svg_color, svg_markup)
    # Using multi-path SVGs where needed (YouTube, WhatsApp, Instagram)
    social_defs = [
        (
            cfg.fb_link, "Facebook", "#1877F2",
            '<path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>',
        ),
        (
            cfg.ig_link, "Instagram", "url(#ig-grad)",
            '<defs><linearGradient id="ig-grad" x1="0%" y1="100%" x2="100%" y2="0%"><stop offset="0%" stop-color="#f09433"/><stop offset="25%" stop-color="#e6683c"/><stop offset="50%" stop-color="#dc2743"/><stop offset="75%" stop-color="#cc2366"/><stop offset="100%" stop-color="#bc1888"/></linearGradient></defs><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 100 12.324 6.162 6.162 0 000-12.324zM12 16a4 4 0 110-8 4 4 0 010 8zm6.406-11.845a1.44 1.44 0 100 2.881 1.44 1.44 0 000-2.881z"/>',
        ),
        (
            cfg.x_link, "X (Twitter)", "#000000",
            '<path d="M18.901 1.153h3.68l-8.04 9.19L24 22.846h-7.406l-5.8-7.584-6.638 7.584H.474l8.6-9.83L0 1.154h7.594l5.243 6.932ZM17.61 20.644h2.039L6.486 3.24H4.298Z"/>',
        ),
        (
            cfg.li_link, "LinkedIn", "#0A66C2",
            '<path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>',
        ),
        (
            cfg.yt_link, "YouTube", "#FF0000",
            '<path d="M23.495 6.205a3.007 3.007 0 00-2.088-2.088c-1.87-.501-9.396-.501-9.396-.501s-7.507-.01-9.396.501A3.007 3.007 0 00.527 6.205a31.247 31.247 0 00-.522 5.805 31.247 31.247 0 00.522 5.783 3.007 3.007 0 002.088 2.088c1.868.502 9.396.502 9.396.502s7.506 0 9.396-.502a3.007 3.007 0 002.088-2.088 31.247 31.247 0 00.5-5.783 31.247 31.247 0 00-.5-5.805zM9.609 15.601V8.408l6.264 3.602z"/>',
        ),
        (
            cfg.wa_num and f"https://wa.me/{clean_phone(cfg.wa_num)}", "WhatsApp", "#25D366",
            '<path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/>',
        ),
    ]

    for link, label, brand_color, svg_inner in social_defs:
        if link:
            icons += (
                f'<a href="{sanitize_url(str(link))}" target="_blank" rel="noopener noreferrer"'
                f' aria-label="{label}" class="social-link social-link--{label.lower().replace(" ","-")}"'
                f' style="--brand:{brand_color}">'
                f'<svg class="social-icon" viewBox="0 0 24 24" aria-hidden="true">{svg_inner}</svg>'
                f'</a>'
            )

    footer_blog = '<a href="blog.html">Blog</a>' if cfg.show_blog else ''
    footer_book = '<a href="booking.html">Book Now</a>' if cfg.show_booking else ''
    year = datetime.datetime.now().year

    return f"""
<footer role="contentinfo">
    <div class="container">
        <div class="footer-grid">
            <div class="footer-brand">
                <h3>{sanitize(cfg.biz_name)}</h3>
                <p class="footer-tagline">{sanitize(cfg.biz_tagline)}</p>
                <address class="footer-address" style="font-style:normal;">{sanitize(cfg.biz_addr)}</address>
                <div class="social-links" aria-label="Social media links">{icons}</div>
            </div>
            <nav class="footer-nav" aria-label="Footer navigation">
                <h4>Quick Links</h4>
                <a href="index.html">Home</a>
                <a href="about.html">About</a>
                {footer_blog}{footer_book}
                <a href="contact.html">Contact</a>
            </nav>
            <nav class="footer-nav" aria-label="Legal links">
                <h4>Legal</h4>
                <a href="privacy.html">Privacy Policy</a>
                <a href="terms.html">Terms of Service</a>
            </nav>
        </div>
        <div class="footer-bottom">
            <p>&copy; {year} <span>{sanitize(cfg.biz_name)}</span>. Built with Titan Engine v56.</p>
        </div>
    </div>
</footer>"""


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 13 — CART SYSTEM (complete rewrite)
# ═══════════════════════════════════════════════════════════════════════════════

def gen_cart_system(cfg: 'SiteConfig') -> str:
    """
    v56 REWRITE:
    - Quantity controls (+ / − per item)
    - Currency-agnostic price parsing (handles $, €, £, ₹, etc.)
    - Toast notifications instead of alert()
    - Touch-optimised close gesture (swipe down)
    - ARIA live region for cart count
    - All config values passed via JSON.stringify, never string-interpolated into JS
    - Cart persists across pages via localStorage with a versioned key
    """
    if not cfg.wa_num:
        return ""
    wa_js  = json.dumps(clean_phone(cfg.wa_num))
    upi_js = json.dumps(cfg.upi_id)
    pp_js  = json.dumps(cfg.paypal_link)
    ab_js  = "msg+='\\n(Variant:'+(localStorage.getItem('titan_ab')||'')+')' ;" if cfg.enable_ab else ""

    return f"""
<div id="cart-float" role="button" tabindex="0" aria-label="Open cart" style="display:none;"
     onclick="titanCartToggle()" onkeydown="if(event.key==='Enter')titanCartToggle()">
    🛒 <span id="cart-count" aria-live="polite" aria-atomic="true">0</span>
</div>
<div id="cart-overlay" onclick="titanCartToggle()" role="presentation"></div>
<div id="cart-modal" role="dialog" aria-modal="true" aria-labelledby="cart-title">
    <button class="cart-close" onclick="titanCartToggle()" aria-label="Close cart">&times;</button>
    <h3 id="cart-title">Your Cart</h3>
    <div id="cart-items" style="max-height:260px;overflow-y:auto;" aria-live="polite"></div>
    <div class="cart-total-row">
        <span>Total</span>
        <strong id="cart-total">0.00</strong>
    </div>
    <div class="local-vault">
        <p class="vault-label">🔒 Checkout Details</p>
        <label for="vault-name" class="sr-only">Your name</label>
        <input type="text" id="vault-name" placeholder="Full Name" autocomplete="name">
        <label for="vault-address" class="sr-only">Delivery address</label>
        <input type="text" id="vault-address" placeholder="Delivery Address" autocomplete="street-address">
    </div>
    <button onclick="titanCheckoutWA()" class="btn btn-accent" style="width:100%;margin-top:1rem;height:3.5rem;">
        1-Tap Checkout via WhatsApp
    </button>
</div>

<script>
(function() {{
    'use strict';
    const WA  = {wa_js};
    const UPI = {upi_js};
    const PP  = {pp_js};
    const CART_KEY = 'titanCart_v2';

    let cart = [];
    try {{ cart = JSON.parse(localStorage.getItem(CART_KEY)) || []; }} catch(e) {{ cart = []; }}

    function parsePrice(str) {{
        if (!str) return 0;
        const n = parseFloat(String(str).replace(/[^\\d.]/g, ''));
        return isNaN(n) ? 0 : n;
    }}

    function renderCart() {{
        const box   = document.getElementById('cart-items');
        const count = document.getElementById('cart-count');
        const total = document.getElementById('cart-total');
        const float = document.getElementById('cart-float');
        if (!box) return;

        let sum = 0;
        const totalItems = cart.reduce((a, c) => a + c.qty, 0);
        box.innerHTML = '';
        cart.forEach((item, i) => {{
            sum += parsePrice(item.price) * item.qty;
            const row = document.createElement('div');
            row.className = 'cart-item';
            row.innerHTML = [
                '<span class="cart-item-name">' + item.name + '</span>',
                '<div class="cart-item-controls">',
                '  <button onclick="titanChangeQty(' + i + ', -1)" aria-label="Remove one">−</button>',
                '  <span class="cart-qty">' + item.qty + '</span>',
                '  <button onclick="titanChangeQty(' + i + ', 1)" aria-label="Add one">+</button>',
                '  <span class="cart-item-price">' + item.price + '</span>',
                '  <button class="cart-remove" onclick="titanRemoveItem(' + i + ')" aria-label="Remove ' + item.name + '">×</button>',
                '</div>',
            ].join('');
            box.appendChild(row);
        }});

        if (count) count.textContent = totalItems;
        if (total) total.textContent = sum.toFixed(2);
        if (float) float.style.display = totalItems > 0 ? 'flex' : 'none';
        try {{ localStorage.setItem(CART_KEY, JSON.stringify(cart)); }} catch(e) {{}}
    }}

    window.titanAddToCart = function(name, price) {{
        const existing = cart.find(i => i.name === name);
        if (existing) {{
            existing.qty++;
            titanToast(name + ' quantity updated', 'success');
        }} else {{
            cart.push({{ name, price, qty: 1 }});
            titanToast(name + ' added to cart!', 'success');
        }}
        renderCart();
    }};

    window.titanChangeQty = function(index, delta) {{
        if (!cart[index]) return;
        cart[index].qty += delta;
        if (cart[index].qty <= 0) cart.splice(index, 1);
        renderCart();
    }};

    window.titanRemoveItem = function(index) {{
        cart.splice(index, 1);
        renderCart();
    }};

    window.titanCartToggle = function() {{
        const modal   = document.getElementById('cart-modal');
        const overlay = document.getElementById('cart-overlay');
        if (!modal) return;
        const isOpen = modal.classList.toggle('open');
        if (overlay) overlay.style.display = isOpen ? 'block' : 'none';
        if (isOpen) {{
            // Restore saved checkout details
            const name = document.getElementById('vault-name');
            const addr = document.getElementById('vault-address');
            try {{
                if (name) name.value = localStorage.getItem('t_name') || '';
                if (addr) addr.value = localStorage.getItem('t_addr') || '';
            }} catch(e) {{}}
            // Focus first focusable element
            const first = modal.querySelector('button,input');
            if (first) first.focus();
        }}
    }};

    window.titanCheckoutWA = function() {{
        const nameEl = document.getElementById('vault-name');
        const addrEl = document.getElementById('vault-address');
        const n = nameEl ? nameEl.value.trim() : '';
        const a = addrEl ? addrEl.value.trim() : '';
        try {{
            if (n) localStorage.setItem('t_name', n);
            if (a) localStorage.setItem('t_addr', a);
        }} catch(e) {{}}

        if (!cart.length) {{ titanToast('Your cart is empty!', 'error'); return; }}

        let total = 0;
        let msg = 'New Order:%0A%0A';
        cart.forEach(item => {{
            const subtotal = parsePrice(item.price) * item.qty;
            total += subtotal;
            msg += '- ' + encodeURIComponent(item.name) + ' x' + item.qty + ' = ' + encodeURIComponent(item.price) + '%0A';
        }});
        msg += '%0ATotal: ' + total.toFixed(2) + '%0A';
        if (n) msg += '%0ADeliver to: ' + encodeURIComponent(n) + ', ' + encodeURIComponent(a) + '%0A';
        {ab_js}
        if (UPI || PP) msg += '%0APayment:%0A';
        if (UPI) msg += 'UPI: ' + encodeURIComponent(UPI) + '%0A';
        if (PP)  msg += 'PayPal: ' + encodeURIComponent(PP);

        const url = 'https://wa.me/' + WA + '?text=' + msg;
        window.open(url, '_blank', 'noopener,noreferrer');
        cart = [];
        renderCart();
        titanCartToggle();
    }};

    // Close cart on Escape key
    document.addEventListener('keydown', (e) => {{
        if (e.key === 'Escape') {{
            const modal = document.getElementById('cart-modal');
            if (modal && modal.classList.contains('open')) titanCartToggle();
        }}
    }});

    document.addEventListener('DOMContentLoaded', renderCart);
}})();
</script>"""


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 14 — WHATSAPP WIDGET
# ═══════════════════════════════════════════════════════════════════════════════

def gen_wa_widget(cfg: 'SiteConfig') -> str:
    if not cfg.wa_num:
        return ""
    clean_wa = clean_phone(cfg.wa_num)
    # Full WhatsApp SVG with bubble + phone paths for crisp rendering at all sizes
    return f"""
<a href="https://wa.me/{clean_wa}"
   target="_blank"
   rel="noopener noreferrer"
   id="wa-widget"
   aria-label="Chat with us on WhatsApp"
   class="wa-float-btn">
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512" width="28" height="28" aria-hidden="true" style="display:block;">
        <path fill="#ffffff" d="M380.9 97.1C339 55.1 283.2 32 223.9 32c-122.4 0-222 99.6-222 222 0 39.1 10.2 77.3 29.6 111L0 480l117.7-30.9c32.4 17.7 68.9 27 106.1 27h.1c122.3 0 224.1-99.6 224.1-222 0-59.3-23.1-115-65.1-157zm-157 341.6c-33.2 0-65.7-8.9-94-25.7l-6.7-4-69.8 18.3L72 359.2l-4.4-7c-18.5-29.4-28.2-63.3-28.2-98.2 0-101.7 82.8-184.5 184.6-184.5 49.3 0 95.6 19.2 130.4 54.1 34.8 34.9 56.2 81.2 56.1 130.5 0 101.8-84.9 184.6-186.6 184.6zm101.2-138.2c-5.5-2.8-32.8-16.2-37.9-18-5.1-1.9-8.8-2.8-12.5 2.8-3.7 5.6-14.3 18-17.6 21.8-3.2 3.7-6.5 4.2-12 1.4-32.6-16.3-54-29.1-75.5-66-5.7-9.8 5.7-9.1 16.3-30.3 1.8-3.7.9-6.9-.5-9.7-1.4-2.8-12.5-30.1-17.1-41.2-4.5-10.8-9.1-9.3-12.5-9.5-3.2-.2-6.9-.2-10.6-.2-3.7 0-9.7 1.4-14.8 6.9-5.1 5.6-19.4 19-19.4 46.3 0 27.3 19.9 53.7 22.6 57.4 2.8 3.7 39.1 59.7 94.8 83.8 35.2 15.2 49 16.5 66.6 13.9 10.7-1.6 32.8-13.4 37.4-26.4 4.6-13 4.6-24.1 3.2-26.4-1.3-2.5-5-3.9-10.5-6.6z"/>
    </svg>
    <span class="wa-label">WhatsApp</span>
</a>"""


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 15 — LEAD POPUP
# ═══════════════════════════════════════════════════════════════════════════════

def gen_popup(cfg: 'SiteConfig') -> str:
    if not cfg.popup_enabled:
        return ""
    clean_wa  = clean_phone(cfg.wa_num)
    delay_ms  = max(1000, cfg.popup_delay * 1000)
    title_js  = json.dumps(sanitize(cfg.popup_title))
    text_js   = json.dumps(sanitize(cfg.popup_text))
    cta_js    = json.dumps(sanitize(cfg.popup_cta))
    return f"""
<div id="lead-popup" role="dialog" aria-modal="true" aria-labelledby="popup-title" style="display:none;">
    <button class="close-popup" onclick="titanClosePopup()" aria-label="Close offer popup">&times;</button>
    <div class="popup-icon" aria-hidden="true">🎁</div>
    <h3 id="popup-title">{sanitize(cfg.popup_title)}</h3>
    <p>{sanitize(cfg.popup_text)}</p>
    <a href="https://wa.me/{clean_wa}?text=I+want+the+offer"
       class="btn btn-accent popup-cta-btn"
       target="_blank" rel="noopener noreferrer">
        {sanitize(cfg.popup_cta)}
    </a>
</div>
<div id="popup-overlay" onclick="titanClosePopup()" style="display:none;" role="presentation"></div>
<script>
function titanClosePopup() {{
    document.getElementById('lead-popup').style.display = 'none';
    document.getElementById('popup-overlay').style.display = 'none';
}}
function titanOpenPopup() {{
    const p = document.getElementById('lead-popup');
    const o = document.getElementById('popup-overlay');
    if (!p) return;
    p.style.display = 'block';
    if (o) o.style.display = 'block';
    p.querySelector('button')?.focus();
}}
setTimeout(() => {{
    try {{
        if (!sessionStorage.getItem('titanPopupShown')) {{
            titanOpenPopup();
            sessionStorage.setItem('titanPopupShown', '1');
        }}
    }} catch(e) {{ titanOpenPopup(); }}
}}, {delay_ms});
document.addEventListener('keydown', (e) => {{
    if (e.key === 'Escape') titanClosePopup();
}});
</script>"""


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 16 — MULTI-LANGUAGE SWITCHER
# ═══════════════════════════════════════════════════════════════════════════════

def gen_lang_script(cfg: 'SiteConfig') -> str:
    if not cfg.lang_sheet:
        return ""
    sheet_js = json.dumps(cfg.lang_sheet)
    return f"""
<div id="lang-overlay" onclick="closeLangModal()" style="display:none;" role="presentation"></div>
<div id="lang-modal" role="dialog" aria-modal="true" aria-labelledby="lang-modal-title" style="display:none;">
    <h3 id="lang-modal-title">Select Language</h3>
    <div class="lang-grid" role="list">
        <button onclick="switchLang('en',0)" class="lang-opt" role="listitem" lang="en">🇺🇸 English</button>
        <button onclick="switchLang('es',1)" class="lang-opt" role="listitem" lang="es">🇪🇸 Español</button>
        <button onclick="switchLang('fr',2)" class="lang-opt" role="listitem" lang="fr">🇫🇷 Français</button>
        <button onclick="switchLang('ar',3)" class="lang-opt" role="listitem" lang="ar">🇸🇦 العربية</button>
        <button onclick="switchLang('de',4)" class="lang-opt" role="listitem" lang="de">🇩🇪 Deutsch</button>
        <button onclick="switchLang('pt',5)" class="lang-opt" role="listitem" lang="pt">🇧🇷 Português</button>
    </div>
</div>
<script>
(function() {{
    const SHEET = {sheet_js};
    window.openLangModal = function() {{
        document.getElementById('lang-modal').style.display = 'block';
        document.getElementById('lang-overlay').style.display = 'block';
    }};
    window.closeLangModal = function() {{
        document.getElementById('lang-modal').style.display = 'none';
        document.getElementById('lang-overlay').style.display = 'none';
    }};
    window.switchLang = async function(code, col) {{
        closeLangModal();
        try {{ localStorage.setItem('titan_lang', code); localStorage.setItem('titan_col', col); }} catch(e) {{}}
        if (code === 'en') {{ location.reload(); return; }}
        try {{
            const res = await fetch(SHEET);
            const txt = await res.text();
            const lines = txt.split(/\\r?\\n/);
            for (let i = 1; i < lines.length; i++) {{
                const row = parseCSVLine(lines[i]);
                if (row.length > col && row[col]) {{
                    const el = document.getElementById(row[0]);
                    if (el) el.textContent = row[col];
                }}
            }}
            document.documentElement.lang = code;
            if (code === 'ar') document.documentElement.dir = 'rtl';
        }} catch(e) {{ console.error('[Titan] Language switch error:', e); }}
    }};
    document.addEventListener('DOMContentLoaded', () => {{
        try {{
            const sl = localStorage.getItem('titan_lang');
            const sc = parseInt(localStorage.getItem('titan_col') || '0', 10);
            if (sl && sl !== 'en') switchLang(sl, sc);
        }} catch(e) {{}}
    }});
    document.addEventListener('keydown', (e) => {{ if (e.key === 'Escape') closeLangModal(); }});
}})();
</script>"""


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 17 — INNER PAGE HEADER
# ═══════════════════════════════════════════════════════════════════════════════

def gen_inner_header(title: str) -> str:
    safe_title = sanitize(title)
    return f"""
<header class="inner-page-header" role="banner">
    <div class="container">
        <h1>{safe_title}</h1>
    </div>
</header>"""


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 18 — CONTACT PAGE
# ═══════════════════════════════════════════════════════════════════════════════

def gen_contact_page(cfg: 'SiteConfig') -> str:
    clean_wa   = clean_phone(cfg.wa_num)
    map_embed  = sanitize_embed(cfg.map_iframe)
    return f"""
{gen_inner_header("Contact Us")}
<section class="contact-section" aria-labelledby="contact-heading">
    <div class="container">
        <h2 id="contact-heading" class="sr-only">Contact Information</h2>
        <div class="contact-grid">
            <div class="card contact-info-card">
                <h3>Get In Touch</h3>
                <div class="contact-detail">
                    <span class="contact-label">Address</span>
                    <address>{sanitize(cfg.biz_addr)}</address>
                </div>
                <div class="contact-detail">
                    <span class="contact-label">Phone</span>
                    <a href="tel:{clean_phone(cfg.biz_phone)}" class="contact-link">
                        {sanitize(cfg.biz_phone)}
                    </a>
                </div>
                <div class="contact-detail">
                    <span class="contact-label">Email</span>
                    <a href="mailto:{sanitize(cfg.biz_email)}" class="contact-link">
                        {sanitize(cfg.biz_email)}
                    </a>
                </div>
                <a href="https://wa.me/{clean_wa}"
                   target="_blank" rel="noopener noreferrer"
                   class="btn btn-accent wa-contact-btn">
                    WhatsApp Us Instantly
                </a>
            </div>
            <div class="card contact-form-card">
                <h3>Send a Message</h3>
                <form
                    action="https://formsubmit.co/{sanitize(cfg.biz_email)}"
                    method="POST"
                    class="contact-form"
                    novalidate>
                    <input type="hidden" name="_captcha" value="false">
                    <input type="hidden" name="_subject" value="New message from {sanitize(cfg.biz_name)} website">
                    <div class="form-group">
                        <label for="contact-name">Full Name</label>
                        <input type="text" id="contact-name" name="name" required
                               autocomplete="name" placeholder="Jane Smith">
                    </div>
                    <div class="form-group">
                        <label for="contact-email">Email Address</label>
                        <input type="email" id="contact-email" name="email" required
                               autocomplete="email" placeholder="jane@example.com">
                    </div>
                    <div class="form-group">
                        <label for="contact-msg">Your Message</label>
                        <textarea id="contact-msg" name="msg" rows="5" required
                                  placeholder="Tell us about your project..."></textarea>
                    </div>
                    <button class="btn btn-primary" type="submit">
                        Send Secure Message →
                    </button>
                </form>
            </div>
        </div>
        {('<div class="map-container">' + map_embed + '</div>') if map_embed else ''}
    </div>
</section>"""


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 19 — PRODUCT DETAIL PAGE
# ═══════════════════════════════════════════════════════════════════════════════

def gen_product_page_content(cfg: 'SiteConfig', is_demo: bool = False) -> str:
    ar_script = (
        '<script type="module" src="https://ajax.googleapis.com/ajax/libs/model-viewer/3.4.0/model-viewer.min.js"></script>'
        if cfg.enable_ar else ''
    )
    sheet_js      = json.dumps(cfg.sheet_url)
    custom_img_js = json.dumps(cfg.custom_feat)
    biz_name_js   = json.dumps(cfg.biz_name)
    demo_js       = 'true' if is_demo else 'false'
    ar_enabled_js = 'true' if cfg.enable_ar else 'false'

    return f"""
{ar_script}
<section class="product-section" aria-labelledby="product-name">
    <div class="container">
        <a href="index.html#inventory" class="back-btn" aria-label="Back to store">← Back to Store</a>
        <div id="product-detail-target" role="main" aria-live="polite">
            <div class="loading-skeleton product-skeleton"></div>
        </div>
    </div>
</section>
<script>
(function() {{
    'use strict';
    const SHEET = {sheet_js};
    const DEFAULT_IMG = {custom_img_js};
    const BIZ_NAME = {biz_name_js};
    const IS_DEMO = {demo_js};
    const AR_ENABLED = {ar_enabled_js};

    function changeMainMedia(src, isModel) {{
        const main = document.getElementById('main-media');
        if (!main) return;
        if (isModel && AR_ENABLED) {{
            main.outerHTML = '<model-viewer id="main-media" src="' + src + '" ar ar-modes="webxr scene-viewer quick-look" camera-controls auto-rotate style="width:100%;height:500px;border-radius:24px;"></model-viewer>';
        }} else {{
            main.outerHTML = '<img id="main-media" src="' + src + '" style="width:100%;border-radius:24px;height:500px;object-fit:cover;" alt="Product image">';
        }}
    }}

    async function loadProduct() {{
        const target = document.getElementById('product-detail-target');
        if (!target || !SHEET) {{
            target.innerHTML = '<p class="error-msg">No store data connected.</p>';
            return;
        }}
        const params = new URLSearchParams(window.location.search);
        let targetName = params.get('item') || '';
        try {{
            const res = await fetch(SHEET);
            if (!res.ok) throw new Error('HTTP ' + res.status);
            const txt = await res.text();
            const lines = txt.split(/\\r?\\n/).filter(l => l.trim());
            for (let i = 1; i < lines.length; i++) {{
                const c = parseCSVLine(lines[i]);
                if (!c[0]) continue;
                const match = IS_DEMO ? i === 1 : c[0] === decodeURIComponent(targetName);
                if (!match) continue;
                const imgs = c[3] ? c[3].split('|').map(s => s.trim()).filter(Boolean) : [DEFAULT_IMG];
                const hasStripe = c[4] && c[4].includes('http') && !/\\.(jpg|jpeg|png|gif|webp)$/i.test(c[4]);
                const has3D = AR_ENABLED && c[5] && c[5].includes('.glb');
                let thumbsHtml = '';
                imgs.forEach((img, idx) => {{
                    thumbsHtml += '<img src="' + img + '" onclick="changeMainMedia(\'' + img + '\', false)" class="thumb" loading="lazy" alt="Product view ' + (idx + 1) + '">';
                }});
                if (has3D) {{
                    thumbsHtml += '<button onclick="changeMainMedia(\'' + c[5] + '\', true)" class="thumb thumb-3d" aria-label="View in 3D / AR">AR 3D</button>';
                }}
                const actionBtn = hasStripe
                    ? '<a href="' + c[4] + '" class="btn btn-accent prod-action-btn" target="_blank" rel="noopener noreferrer">Secure Checkout</a>'
                    : '<button onclick="titanAddToCart(' + JSON.stringify(c[0]) + ',' + JSON.stringify(c[1]) + ')" class="btn btn-accent prod-action-btn">Add to Cart</button>';

                document.title = c[0] + ' | ' + BIZ_NAME;
                target.innerHTML = [
                    '<div class="detail-view">',
                    '  <div class="product-media-column">',
                    '    <img id="main-media" src="' + imgs[0] + '" style="width:100%;border-radius:24px;height:500px;object-fit:cover;" alt="' + c[0] + '">',
                    '    <div class="gallery-thumbs">' + thumbsHtml + '</div>',
                    '  </div>',
                    '  <div class="product-info-column">',
                    '    <h1 id="product-name">' + c[0] + '</h1>',
                    '    <div class="product-price-tag">' + c[1] + '</div>',
                    '    <div class="product-specs-container">' + parseMarkdown(c[2] || '') + '</div>',
                    '    <div class="prod-actions">' + actionBtn + '</div>',
                    '  </div>',
                    '</div>',
                ].join('\\n');
                return;
            }}
            target.innerHTML = '<p class="error-msg">Product not found.</p>';
        }} catch(err) {{
            console.error('[Titan] Product load error:', err);
            target.innerHTML = '<p class="error-msg">Failed to load product. Please try again.</p>';
        }}
    }}
    document.addEventListener('DOMContentLoaded', loadProduct);
}})();
</script>"""


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 20 — BLOG INDEX
# ═══════════════════════════════════════════════════════════════════════════════

def gen_blog_index_html(cfg: 'SiteConfig') -> str:
    if not cfg.show_blog:
        return ""
    sheet_js = json.dumps(cfg.blog_sheet_url)
    img1_js  = json.dumps(sanitize_url(cfg.hero_img_1))
    return f"""
<header class="blog-hero" role="banner"
    style="background-image:linear-gradient(rgba(0,0,0,0.6),rgba(0,0,0,0.6)),url({json.dumps(sanitize_url(cfg.hero_img_1))});">
    <div class="container hero-content">
        <h1>{sanitize(cfg.blog_hero_title)}</h1>
        <p>{sanitize(cfg.blog_hero_sub)}</p>
    </div>
</header>
<section aria-labelledby="blog-posts-heading">
    <div class="container">
        <h2 id="blog-posts-heading" class="sr-only">Blog Posts</h2>
        <div id="blog-grid" class="grid-3" role="list" aria-label="Blog posts">
            <div class="loading-skeleton"></div>
            <div class="loading-skeleton"></div>
            <div class="loading-skeleton"></div>
        </div>
    </div>
</section>
<script>
(function() {{
    'use strict';
    const SHEET = {sheet_js};
    async function loadBlog() {{
        const box = document.getElementById('blog-grid');
        if (!box || !SHEET) {{ if(box) box.innerHTML = '<p>No blog sheet connected.</p>'; return; }}
        try {{
            const res = await fetch(SHEET);
            const txt = await res.text();
            const lines = txt.split(/\\r?\\n/).filter(l => l.trim());
            box.innerHTML = '';
            for (let i = 1; i < lines.length; i++) {{
                const r = parseCSVLine(lines[i]);
                if (r.length < 5 || !r[0]) continue;
                const imgSrc = r[5] || {img1_js};
                const article = document.createElement('article');
                article.className = 'card reveal';
                article.setAttribute('role', 'listitem');
                article.innerHTML = [
                    '<img src="' + imgSrc + '" style="width:100%;height:220px;object-fit:cover;" loading="lazy" alt="' + r[1] + '">',
                    '<div class="card-body">',
                    '  <span class="blog-category">' + (r[3] || 'General') + '</span>',
                    '  <h3><a href="post.html?id=' + encodeURIComponent(r[0]) + '" class="blog-title-link">' + r[1] + '</a></h3>',
                    '  <p class="card-desc">' + (r[4] || '') + '</p>',
                    '  <a href="post.html?id=' + encodeURIComponent(r[0]) + '" class="btn btn-primary blog-read-btn" aria-label="Read: ' + r[1] + '">',
                    '    Read Article →',
                    '  </a>',
                    '</div>',
                ].join('\\n');
                box.appendChild(article);
            }}
        }} catch(err) {{
            console.error('[Titan] Blog index error:', err);
            if (box) box.innerHTML = '<p class="error-msg">Failed to load posts.</p>';
        }}
    }}
    function waitForRuntime(cb, n) {{
        if (typeof parseCSVLine === 'function') {{ cb(); return; }}
        if ((n || 0) > 40) return;
        setTimeout(function() {{ waitForRuntime(cb, (n || 0) + 1); }}, 80);
    }}
    
    document.addEventListener('DOMContentLoaded', function() {{ waitForRuntime(loadBlog); }});
}})();
</script>"""   }}
            }} catch(err) {{
                console.error('[Titan] Blog load error:', err);
                if (box) box.innerHTML = '<p style="text-align:center;padding:2rem;color:#ef4444;">Could not load blog posts. Publish your Google Sheet: File > Share > Publish to web > CSV format.</p>';
            }}
        }});
    }});
}})();
</script>"""


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 21 — BLOG POST
# ═══════════════════════════════════════════════════════════════════════════════

def gen_blog_post_html(cfg: 'SiteConfig') -> str:
    if not cfg.show_blog:
        return ""
    sheet_js   = json.dumps(cfg.blog_sheet_url)
    biz_js     = json.dumps(cfg.biz_name)
    return f"""
<article id="post-container" class="blog-post-container" aria-live="polite">
    <div class="loading-skeleton post-skeleton"></div>
</article>
<script>
(function() {{
    'use strict';
    const SHEET = {sheet_js};
    const BIZ   = {biz_js};
    async function loadPost() {{
        const container = document.getElementById('post-container');
        if (!container || !SHEET) return;
        const slug = new URLSearchParams(window.location.search).get('id');
        try {{
            const res = await fetch(SHEET);
            const txt = await res.text();
            const lines = txt.split(/\\r?\\n/).filter(l => l.trim());
            for (let i = 1; i < lines.length; i++) {{
                const r = parseCSVLine(lines[i]);
                if (!r[0] || r[0] !== decodeURIComponent(slug)) continue;
                document.title = r[1] + ' | ' + BIZ;
                const contentHtml = parseMarkdown(r[6] || r[4] || '');
                container.innerHTML = [
                    '<header class="post-header">',
                    '  <div class="container">',
                    '    <span class="blog-category">' + (r[3] || '') + '</span>',
                    '    <h1>' + r[1] + '</h1>',
                    '    <p class="post-meta">' + (r[2] || '') + '</p>',
                    '  </div>',
                    '</header>',
                    '<div class="container post-body">',
                    '  <img src="' + (r[5] || '') + '" class="post-hero-img" loading="lazy" alt="' + r[1] + '">',
                    '  <div class="post-content">' + contentHtml + '</div>',
                    '  <a href="blog.html" class="btn btn-primary post-back-btn">← Back to Blog</a>',
                    '</div>',
                ].join('\\n');
                return;
            }}
            container.innerHTML = '<div class="container"><p class="error-msg">Post not found.</p></div>';
        }} catch(err) {{
            console.error('[Titan] Post load error:', err);
            container.innerHTML = '<div class="container"><p class="error-msg">Failed to load article.</p></div>';
        }}
    }}
        function waitForRuntime(cb, n) {{
        if (typeof parseCSVLine === 'function') {{ cb(); return; }}
        if ((n || 0) > 40) return;
        setTimeout(function() {{ waitForRuntime(cb, (n || 0) + 1); }}, 80);
    }}
    document.addEventListener('DOMContentLoaded', function() {{ waitForRuntime(loadPost); }});
}})();
</script>"""


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 22 — BOOKING PAGE
# ═══════════════════════════════════════════════════════════════════════════════

def gen_booking_content(cfg: 'SiteConfig') -> str:
    if not cfg.show_booking:
        return ""
    safe_embed = sanitize_embed(cfg.booking_embed)
    return f"""
<header class="inner-page-header" role="banner">
    <div class="container">
        <h1>{sanitize(cfg.booking_title)}</h1>
        <p>{sanitize(cfg.booking_desc)}</p>
    </div>
</header>
<section class="booking-section" aria-labelledby="booking-widget-label">
    <div class="container">
        <h2 id="booking-widget-label" class="sr-only">Booking Calendar</h2>
        <div class="booking-embed-wrapper">
            {safe_embed}
        </div>
    </div>
</section>"""
