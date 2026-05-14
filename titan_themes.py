# titan_themes.py  — Titan Engine v56 "Flawless"
#
# v56 ARCHITECTURAL CHANGES vs v55:
#
#   1. CONTRAST SAFETY     — generate_modern_css() now calls accessible_text_color()
#                            from utils.py so button labels, nav text, and hero copy
#                            always meet WCAG AA contrast ratios regardless of user
#                            colour picks. No more invisible white text on white buttons.
#
#   2. CONTAINER QUERIES   — .card components use @container queries instead of pure
#                            viewport media queries, enabling true component-level
#                            responsiveness inside any layout context (sidebar, drawer,
#                            full-width). This is the "CSS Grid Subgrid" era pattern.
#
#   3. CART CSS REWRITE    — Cart modal, cart-float, cart-item quantity controls, and
#                            vault inputs all properly styled. v55 had the modal
#                            declared but critical interactive states missing.
#
#   4. FILTER PILLS        — Store category filter pills and the voice search button
#                            are fully styled with focus-visible rings.
#
#   5. CONTACT FORM        — .form-group, label, input, textarea all precisely styled.
#                            Focus states use box-shadow outlines (not border changes)
#                            to avoid layout shift.
#
#   6. BLOG + POST         — .blog-hero, .blog-category, .blog-title-link, .post-header,
#                            .post-body, .post-content, .post-hero-img all defined.
#
#   7. PRICING v56         — .titan-col, .savings-highlight, .savings-row, .savings-cell,
#                            .price-note all defined. Table is accessible with scope attrs.
#
#   8. NAV v56             — .nav-wordmark, .nav-brand, .nav-link underline animation,
#                            .hamburger-line animated to ✕ when .active.
#
#   9. FOOTER v56          — .footer-brand, .footer-tagline, .footer-address,
#                            .social-links, .social-link, .footer-bottom all defined.
#
#  10. POPUP + LANG MODAL  — .popup-icon, .popup-cta-btn, .lang-opt focus states.
#
#  11. INNER PAGES         — .inner-page-header with gradient overlay, .inner-body-section.
#
#  12. TESTIMONIAL v56     — .testi-quote-mark, .testi-quote, .testi-author, .testi-name,
#                            .testi-role, .testi-avatar all defined.
#
#  13. BOOKING             — .booking-section, .booking-embed-wrapper.
#
#  14. PRODUCT DETAIL v56  — .prod-actions, .prod-action-btn, .thumb-3d.
#
#  15. DARK MODE           — Extends v55's system with cart, popup, form inputs,
#                            filter pills all covered by dark mode variable overrides.

import re
from utils import accessible_text_color, alpha_hex, darken_hex

# ─────────────────────────────────────────────────────────────────────────────
# THEME REGISTRY  (25 themes — unchanged palette values from v55)
# ─────────────────────────────────────────────────────────────────────────────

THEME_REGISTRY = {
    "1. Stripe Cloud (Modern SaaS)":   {"bg":"#f8fafc","txt":"#0f172a","card":"#ffffff","p":"#6366f1","s":"#10b981","nav":"rgba(255,255,255,0.8)","shadow":"0 10px 40px -10px rgba(99,102,241,0.15)","radius":"16px","border":"1px solid #e2e8f0","dk_bg":"#0f0f1a","dk_card":"#1a1a2e","dk_txt":"#e2e8f0","dk_nav":"rgba(15,15,26,0.85)"},
    "2. Vercel Dark (Developer Core)": {"bg":"#000000","txt":"#ededed","card":"#111111","p":"#ffffff","s":"#0070f3","nav":"rgba(0,0,0,0.8)","shadow":"0 0 0 1px #333","radius":"8px","border":"1px solid #333","dk_bg":"#000000","dk_card":"#0a0a0a","dk_txt":"#ededed","dk_nav":"rgba(0,0,0,0.9)"},
    "3. Apple Minimalist (Pure Clean)":{"bg":"#fbfbfd","txt":"#1d1d1f","card":"#ffffff","p":"#000000","s":"#0066cc","nav":"rgba(251,251,253,0.8)","shadow":"0 4px 24px rgba(0,0,0,0.04)","radius":"24px","border":"none","dk_bg":"#000000","dk_card":"#1c1c1e","dk_txt":"#f5f5f7","dk_nav":"rgba(0,0,0,0.85)"},
    "4. Neo-Brutalist (Gumroad Style)":{"bg":"#f4f4f0","txt":"#000000","card":"#ffffff","p":"#000000","s":"#ff90e8","nav":"#f4f4f0","shadow":"6px 6px 0px #000000","radius":"0px","border":"3px solid #000000","dk_bg":"#1a1a1a","dk_card":"#222222","dk_txt":"#f4f4f0","dk_nav":"#1a1a1a"},
    "5. Glassmorphism (Translucent)":  {"bg":"linear-gradient(135deg,#e0c3fc 0%,#8ec5fc 100%)","txt":"#1e1e24","card":"rgba(255,255,255,0.25)","p":"#3a0ca3","s":"#ff006e","nav":"rgba(255,255,255,0.1)","shadow":"0 8px 32px 0 rgba(31,38,135,0.37)","radius":"20px","border":"1px solid rgba(255,255,255,0.4)","dk_bg":"linear-gradient(135deg,#1a0533 0%,#0d1b3e 100%)","dk_card":"rgba(255,255,255,0.08)","dk_txt":"#e0d6f0","dk_nav":"rgba(0,0,0,0.3)"},
    "6. Luxury Boutique (High-End)":   {"bg":"#faf9f6","txt":"#2c2a29","card":"#ffffff","p":"#d4af37","s":"#1a1a1a","nav":"rgba(250,249,246,0.9)","shadow":"0 15px 35px rgba(0,0,0,0.05)","radius":"0px","border":"1px solid #eaeaea","dk_bg":"#111008","dk_card":"#1c1a10","dk_txt":"#e8e0cc","dk_nav":"rgba(17,16,8,0.95)"},
    "7. Streetwear Edge (Hypebeast)":  {"bg":"#121212","txt":"#f4f4f4","card":"#1e1e1e","p":"#ff4500","s":"#ffffff","nav":"rgba(18,18,18,0.9)","shadow":"0 20px 40px rgba(255,69,0,0.15)","radius":"4px","border":"1px solid #333","dk_bg":"#080808","dk_card":"#141414","dk_txt":"#f4f4f4","dk_nav":"rgba(8,8,8,0.95)"},
    "8. Organic Eco (Sustainable)":    {"bg":"#f0f4f0","txt":"#2c3e2e","card":"#ffffff","p":"#4a7c59","s":"#f39c12","nav":"rgba(240,244,240,0.9)","shadow":"0 10px 30px rgba(74,124,89,0.08)","radius":"30px","border":"none","dk_bg":"#111a12","dk_card":"#1a2b1c","dk_txt":"#c8d8c0","dk_nav":"rgba(17,26,18,0.95)"},
    "9. Cosmetic Pastel (Beauty)":     {"bg":"#fff5f5","txt":"#5c4a4a","card":"#ffffff","p":"#e8b4b8","s":"#a36b7e","nav":"rgba(255,245,245,0.9)","shadow":"0 12px 24px rgba(232,180,184,0.15)","radius":"20px","border":"1px solid #ffe3e3","dk_bg":"#1a0d0d","dk_card":"#261515","dk_txt":"#f0d8d8","dk_nav":"rgba(26,13,13,0.95)"},
    "10. Tech Hardware (Neon Dark)":   {"bg":"#0d1117","txt":"#c9d1d9","card":"#161b22","p":"#58a6ff","s":"#238636","nav":"rgba(13,17,23,0.9)","shadow":"0 0 20px rgba(88,166,255,0.1)","radius":"12px","border":"1px solid #30363d","dk_bg":"#010409","dk_card":"#0d1117","dk_txt":"#c9d1d9","dk_nav":"rgba(1,4,9,0.95)"},
    "11. Medical Platinum (Trust)":    {"bg":"#ffffff","txt":"#1e293b","card":"#f8fafc","p":"#0284c7","s":"#059669","nav":"rgba(255,255,255,0.95)","shadow":"0 4px 6px -1px rgba(0,0,0,0.05)","radius":"12px","border":"1px solid #e2e8f0","dk_bg":"#0a1520","dk_card":"#0f1e2d","dk_txt":"#cbd5e1","dk_nav":"rgba(10,21,32,0.95)"},
    "12. Dental Aqua (Clean)":         {"bg":"#f0fdfa","txt":"#0f172a","card":"#ffffff","p":"#0d9488","s":"#0284c7","nav":"rgba(240,253,250,0.9)","shadow":"0 10px 25px rgba(13,148,136,0.1)","radius":"16px","border":"1px solid #ccfbf1","dk_bg":"#041510","dk_card":"#081f19","dk_txt":"#ccfbf1","dk_nav":"rgba(4,21,16,0.95)"},
    "13. Fitness Aggressive (Gym)":    {"bg":"#0a0a0a","txt":"#ffffff","card":"#171717","p":"#e11d48","s":"#facc15","nav":"rgba(10,10,10,0.9)","shadow":"0 10px 30px rgba(225,29,72,0.2)","radius":"8px","border":"1px solid #262626","dk_bg":"#000000","dk_card":"#0d0d0d","dk_txt":"#ffffff","dk_nav":"rgba(0,0,0,0.95)"},
    "14. Spa Therapy (Calm)":          {"bg":"#faf5f0","txt":"#4a443c","card":"#ffffff","p":"#bfa58a","s":"#8c735a","nav":"rgba(250,245,240,0.9)","shadow":"0 8px 20px rgba(191,165,138,0.1)","radius":"24px","border":"1px solid #f0e6da","dk_bg":"#1a1410","dk_card":"#241e18","dk_txt":"#e8ddd0","dk_nav":"rgba(26,20,16,0.95)"},
    "15. Yoga Mindfulness":            {"bg":"#fdf8f5","txt":"#333333","card":"#ffffff","p":"#d4a373","s":"#a1c181","nav":"rgba(253,248,245,0.9)","shadow":"0 5px 15px rgba(0,0,0,0.03)","radius":"50px","border":"none","dk_bg":"#16120e","dk_card":"#201a14","dk_txt":"#e8ddd0","dk_nav":"rgba(22,18,14,0.95)"},
    "16. Law Firm Heritage":           {"bg":"#ffffff","txt":"#1f2937","card":"#f9fafb","p":"#1e3a8a","s":"#b45309","nav":"rgba(255,255,255,0.95)","shadow":"0 4px 6px rgba(0,0,0,0.05)","radius":"4px","border":"1px solid #e5e7eb","dk_bg":"#0a0e1a","dk_card":"#111827","dk_txt":"#e5e7eb","dk_nav":"rgba(10,14,26,0.95)"},
    "17. Real Estate Prime":           {"bg":"#111827","txt":"#f3f4f6","card":"#1f2937","p":"#fbbf24","s":"#f9fafb","nav":"rgba(17,24,39,0.9)","shadow":"0 10px 30px rgba(251,191,36,0.1)","radius":"8px","border":"1px solid #374151","dk_bg":"#080c14","dk_card":"#111827","dk_txt":"#f3f4f6","dk_nav":"rgba(8,12,20,0.95)"},
    "18. Construction Industrial":     {"bg":"#f5f5f5","txt":"#1a1a1a","card":"#ffffff","p":"#f59e0b","s":"#000000","nav":"rgba(245,245,245,0.95)","shadow":"0 8px 0px #e5e5e5","radius":"0px","border":"2px solid #000000","dk_bg":"#111111","dk_card":"#1a1a1a","dk_txt":"#e5e5e5","dk_nav":"rgba(17,17,17,0.95)"},
    "19. Architecture Grid":           {"bg":"#ffffff","txt":"#000000","card":"#f4f4f5","p":"#000000","s":"#3b82f6","nav":"#ffffff","shadow":"none","radius":"0px","border":"1px solid #000000","dk_bg":"#0a0a0a","dk_card":"#141414","dk_txt":"#f4f4f5","dk_nav":"#0a0a0a"},
    "20. Agency Bold (Creative)":      {"bg":"#4f46e5","txt":"#ffffff","card":"#4338ca","p":"#f9a8d4","s":"#fde047","nav":"rgba(79,70,229,0.9)","shadow":"0 20px 40px rgba(0,0,0,0.2)","radius":"20px","border":"none","dk_bg":"#1e1b4b","dk_card":"#2e27a8","dk_txt":"#e0e7ff","dk_nav":"rgba(30,27,75,0.95)"},
    "21. Cyberpunk 2077":              {"bg":"#fcee0a","txt":"#000000","card":"#000000","p":"#00ffff","s":"#ff003c","nav":"#fcee0a","shadow":"8px 8px 0px #00ffff","radius":"0px","border":"2px solid #000000","dk_bg":"#0a0800","dk_card":"#000000","dk_txt":"#fcee0a","dk_nav":"#0a0800"},
    "22. Monochromatic Black/White":   {"bg":"#ffffff","txt":"#000000","card":"#ffffff","p":"#000000","s":"#000000","nav":"#ffffff","shadow":"4px 4px 0px #000000","radius":"0px","border":"2px solid #000000","dk_bg":"#000000","dk_card":"#111111","dk_txt":"#ffffff","dk_nav":"#000000"},
    "23. Retro Synthwave":             {"bg":"#2b213a","txt":"#e0d6eb","card":"#181425","p":"#ff007f","s":"#00f0ff","nav":"rgba(43,33,58,0.9)","shadow":"0 0 15px rgba(255,0,127,0.5)","radius":"10px","border":"1px solid #ff007f","dk_bg":"#120d1e","dk_card":"#0e0a16","dk_txt":"#e0d6eb","dk_nav":"rgba(18,13,30,0.95)"},
    "24. Gradient Mesh":               {"bg":"linear-gradient(45deg,#ff9a9e 0%,#fecfef 99%)","txt":"#333","card":"rgba(255,255,255,0.6)","p":"#f77062","s":"#3f51b5","nav":"rgba(255,255,255,0.4)","shadow":"0 8px 32px rgba(0,0,0,0.1)","radius":"30px","border":"1px solid rgba(255,255,255,0.5)","dk_bg":"linear-gradient(45deg,#3d0010 0%,#1a0030 100%)","dk_card":"rgba(255,255,255,0.06)","dk_txt":"#f0d8e0","dk_nav":"rgba(0,0,0,0.4)"},
    "25. Midnight Ocean":              {"bg":"#0f2027","txt":"#d1d5db","card":"#203a43","p":"#2c5364","s":"#38ef7d","nav":"rgba(15,32,39,0.9)","shadow":"0 15px 25px rgba(0,0,0,0.3)","radius":"16px","border":"1px solid #2c5364","dk_bg":"#060f13","dk_card":"#0f2027","dk_txt":"#d1d5db","dk_nav":"rgba(6,15,19,0.95)"},
}


# ─────────────────────────────────────────────────────────────────────────────
# FONT PERFORMANCE
# ─────────────────────────────────────────────────────────────────────────────

def gen_font_preload_html(h_font: str, b_font: str) -> str:
    h_enc = h_font.replace(" ", "+")
    b_enc = b_font.replace(" ", "+")
    url = (
        f"https://fonts.googleapis.com/css2?"
        f"family={h_enc}:wght@400;700;800;900"
        f"&family={b_enc}:wght@300;400;500;600"
        f"&display=swap"
    )
    return f"""<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="preload" as="style" href="{url}">
<link rel="stylesheet" href="{url}" media="print" onload="this.media='all'">
<noscript><link rel="stylesheet" href="{url}"></noscript>"""


def _cls_suppression_block(h_font: str, b_font: str) -> str:
    size_adjust_map = {
        "Space Grotesk":     ("Arial",   "105%", "85%", "15%", "0%"),
        "Montserrat":        ("Arial",   "108%", "86%", "14%", "0%"),
        "Playfair Display":  ("Georgia", "96%",  "84%", "16%", "0%"),
        "Outfit":            ("Arial",   "103%", "87%", "13%", "0%"),
        "Clash Display":     ("Arial",   "107%", "85%", "15%", "0%"),
        "Inter":             ("Arial",   "100%", "90%", "10%", "0%"),
        "Plus Jakarta Sans": ("Arial",   "102%", "88%", "12%", "0%"),
        "Satoshi":           ("Arial",   "101%", "89%", "11%", "0%"),
        "Roboto":            ("Arial",   "100%", "92%",  "8%", "0%"),
    }
    blocks = ""
    for font_name in dict.fromkeys([h_font, b_font]):  # dedup, preserve order
        if font_name not in size_adjust_map:
            continue
        fallback, sa, ascent, descent, line_gap = size_adjust_map[font_name]
        blocks += f"""
@font-face {{
    font-family: '{font_name} Fallback';
    src: local('{fallback}');
    size-adjust: {sa};
    ascent-override: {ascent};
    descent-override: {descent};
    line-gap-override: {line_gap};
}}"""
    return blocks


# ─────────────────────────────────────────────────────────────────────────────
# FLUID TYPE SCALE
# ─────────────────────────────────────────────────────────────────────────────

def _fluid_scale(preferred_rem: float) -> dict[str, str]:
    RATIO = 1.25
    h1 = preferred_rem
    h2 = round(h1 / RATIO, 3)
    h3 = round(h2 / RATIO, 3)
    h4 = round(h3 / RATIO, 3)

    def _clamp(floor: float, pref: float, ceil: float) -> str:
        vw = round((pref * 16) / 13, 4)
        return f"clamp({floor}rem, {vw}vw, {ceil}rem)"

    return {
        "h1":       _clamp(max(1.8,  round(h1 * 0.60, 3)), h1,  round(h1 * 1.15, 3)),
        "h2":       _clamp(max(1.5,  round(h2 * 0.62, 3)), h2,  round(h2 * 1.15, 3)),
        "h3":       _clamp(max(1.2,  round(h3 * 0.65, 3)), h3,  round(h3 * 1.15, 3)),
        "h4":       _clamp(max(1.0,  round(h4 * 0.70, 3)), h4,  round(h4 * 1.12, 3)),
        "stat":     _clamp(2.2, 3.5, 4.5),
        "section_h": _clamp(max(1.4, round(h2 * 0.60, 3)), h2, round(h2 * 1.10, 3)),
    }


def _body_clamp(preferred_rem: float) -> str:
    floor = max(0.875, round(preferred_rem * 0.80, 3))
    ceil  = round(preferred_rem * 1.15, 3)
    vw    = round((preferred_rem * 16) / 13, 4)
    return f"clamp({floor}rem, {vw}vw, {ceil}rem)"


# ─────────────────────────────────────────────────────────────────────────────
# BENTO GRID
# ─────────────────────────────────────────────────────────────────────────────

def _bento_grid_css(theme_name: str, radius: str) -> str:
    is_geometric = any(x in theme_name for x in
                       ["Brutalist","Architecture","Construction","Monochromatic","Cyberpunk"])
    is_organic   = any(x in theme_name for x in
                       ["Yoga","Eco","Spa","Glass","Mesh","Organic","Mindfulness"])

    if is_geometric:
        gap          = "0px"
        card_radius  = "0px"
        card_border  = "2px solid var(--txt-h)"
        card_shadow  = "none"
        hover_tx     = "translate(-4px,-4px)"
        hover_shadow = "8px 8px 0px var(--p)"
    elif is_organic:
        gap          = "clamp(1rem,2.5vw,2.5rem)"
        card_radius  = "clamp(20px,3vw,40px)"
        card_border  = "none"
        card_shadow  = "0 8px 40px -8px rgba(0,0,0,0.08)"
        hover_tx     = "translateY(-8px)"
        hover_shadow = "0 24px 48px -12px rgba(0,0,0,0.12)"
    else:
        gap          = "clamp(1rem,2vw,2rem)"
        card_radius  = radius
        card_border  = "var(--border)"
        card_shadow  = "var(--shadow)"
        hover_tx     = "translateY(-10px)"
        hover_shadow = "0 25px 50px -12px rgba(0,0,0,0.2)"

    return f"""
/* ── BENTO FEATURE GRID ──────────────────────────────────── */
.bento-grid {{
    display: grid;
    grid-template-columns: 2fr 1fr;
    grid-auto-rows: auto;
    gap: {gap};
    align-items: stretch;
    container-type: inline-size;  /* enables @container queries on children */
}}

.bento-card {{
    background:     var(--card);
    border-radius:  {card_radius};
    border:         {card_border};
    box-shadow:     {card_shadow};
    padding:        clamp(1.5rem,3vw,3rem);
    display:        flex;
    flex-direction: column;
    gap:            1.25rem;
    position:       relative;
    overflow:       hidden;
    transition:
        transform   0.35s cubic-bezier(0.175,0.885,0.32,1.275),
        box-shadow  0.35s ease,
        border-color 0.35s ease;
    color:          var(--txt-b);
    /* Container context so child components can use @container */
    container-type: inline-size;
    container-name: bento-cell;
}}

/* Accent top-line appears on hover */
.bento-card::before {{
    content:    '';
    position:   absolute;
    inset:      0 0 auto 0;
    height:     3px;
    background: linear-gradient(90deg, var(--p), var(--s));
    opacity:    0;
    transition: opacity 0.3s;
    z-index:    2;
}}
.bento-card:hover::before {{ opacity: 1; }}
.bento-card:hover {{
    transform:    {hover_tx};
    box-shadow:   {hover_shadow};
    border-color: var(--p);
    z-index:      2;
}}

/* ── SPANNING: card 1 and 4 go full-width ─────────────── */
.bento-grid > .bento-card:nth-child(1) {{
    grid-column:    1 / -1;
    flex-direction: row;
    align-items:    flex-start;
    gap:            clamp(1.5rem,3vw,3rem);
}}
.bento-grid > .bento-card:nth-child(1) .bento-icon {{
    flex-shrink: 0;
    width:  clamp(56px,6vw,80px);
    height: clamp(56px,6vw,80px);
}}
.bento-grid > .bento-card:nth-child(4) {{
    grid-column:    1 / -1;
    flex-direction: row;
    align-items:    center;
    gap:            clamp(1.5rem,3vw,3rem);
    background:     var(--p);
    color:          #fff;
}}
.bento-grid > .bento-card:nth-child(4) h3,
.bento-grid > .bento-card:nth-child(4) p,
.bento-grid > .bento-card:nth-child(4) .bento-icon {{
    color: #fff !important;
    border-color:  rgba(255,255,255,0.2);
    background:    rgba(255,255,255,0.12);
}}
/* Override hover colour inside accent card */
.bento-grid > .bento-card:nth-child(4):hover .bento-icon {{
    background:  rgba(255,255,255,0.25);
    border-color: rgba(255,255,255,0.4);
}}

/* ── ICON WRAPPER ─────────────────────────────────────── */
.bento-icon {{
    width:           clamp(44px,4.5vw,64px);
    height:          clamp(44px,4.5vw,64px);
    border-radius:   calc({card_radius} * 0.6);
    background:      rgba(128,128,128,0.06);
    border:          1px solid rgba(128,128,128,0.12);
    display:         flex;
    align-items:     center;
    justify-content: center;
    color:           var(--s);
    flex-shrink:     0;
    transition:      background 0.3s, color 0.3s, border-color 0.3s;
}}
.bento-card:hover .bento-icon {{
    background:   var(--p);
    color:        #fff;
    border-color: var(--p);
}}

.bento-body {{ display: flex; flex-direction: column; gap: 0.75rem; flex: 1; }}

.bento-card h3 {{
    font-size:      clamp(1.1rem,1.8vw,1.4rem);
    font-weight:    800;
    line-height:    1.2;
    margin-bottom:  0;
    letter-spacing: -0.02em;
    color:          var(--txt-h);
}}

.bento-card p {{
    font-size:   clamp(0.875rem,1.2vw,1rem);
    line-height: 1.7;
    opacity:     0.82;
    margin:      0;
    text-align:  left;
}}

/* ── CONTAINER QUERY: narrow bento cell (<300px wide) ── */
@container bento-cell (max-width: 300px) {{
    .bento-icon {{ width: 40px; height: 40px; }}
    .bento-card h3 {{ font-size: 1rem; }}
}}

/* ── MOBILE COLLAPSE ─────────────────────────────────── */
@media (max-width: 768px) {{
    .bento-grid {{ grid-template-columns: 1fr !important; }}
    .bento-grid > .bento-card:nth-child(1),
    .bento-grid > .bento-card:nth-child(4) {{
        grid-column:    1 / -1;
        flex-direction: column;
    }}
}}

    /* ── PREMIUM BENTO ENHANCEMENTS ──────────────────────── */
    .features-section {{ background: var(--bg); position: relative; overflow: hidden; }}
    .features-bg-grid {{
        position: absolute; inset: 0; pointer-events: none; z-index: 0;
        background-image:
            linear-gradient(rgba(128,128,128,0.045) 1px, transparent 1px),
            linear-gradient(90deg, rgba(128,128,128,0.045) 1px, transparent 1px);
        background-size: 60px 60px;
    }}
    .features-section .container {{ position: relative; z-index: 1; }}
    .section-eyebrow {{
        display: inline-block; padding: 0.3rem 1rem;
        background: var(--p-alpha); color: var(--p); border-radius: 50px;
        font-size: 0.75rem; font-weight: 800; text-transform: uppercase; letter-spacing: 2px;
        margin-bottom: 0.75rem;
    }}
    .bento-card-glow {{
        position: absolute; top: -60px; right: -60px; width: 180px; height: 180px;
        background: radial-gradient(circle, var(--p-alpha) 0%, transparent 70%);
        border-radius: 50%; pointer-events: none; opacity: 0;
        transition: opacity 0.4s ease, transform 0.4s ease; z-index: 0;
    }}
    .bento-card:hover .bento-card-glow {{ opacity: 1; transform: scale(1.4); }}
    .bento-top-row {{
        display: flex; align-items: flex-start; justify-content: space-between;
        margin-bottom: 0.5rem; position: relative; z-index: 1;
    }}
    .bento-meta {{ display: flex; flex-direction: column; align-items: flex-end; gap: 4px; }}
    .bento-num {{
        font-family: var(--h-font); font-size: clamp(1.8rem,2.5vw,2.4rem);
        font-weight: 900; line-height: 1; color: var(--p); opacity: 0.14;
        letter-spacing: -0.04em;
    }}
    .bento-card:hover .bento-num {{ opacity: 0.32; }}
    .bento-tag {{
        padding: 0.2rem 0.6rem; background: var(--s-alpha); color: var(--s);
        border-radius: 50px; font-size: 0.65rem; font-weight: 800;
        text-transform: uppercase; letter-spacing: 1px; white-space: nowrap;
    }}
    .bento-body {{ position: relative; z-index: 1; flex: 1; }}
    .bento-title {{
        font-size: clamp(1.1rem,1.7vw,1.35rem) !important; font-weight: 800 !important;
        line-height: 1.2 !important; color: var(--txt-h) !important;
        letter-spacing: -0.02em !important; margin-bottom: 0.6rem !important;
        position: relative; display: inline-block;
    }}
    .bento-title::after {{
        content: ''; position: absolute; bottom: -2px; left: 0;
        width: 0; height: 2px; background: linear-gradient(90deg, var(--p), var(--s));
        border-radius: 1px; transition: width 0.4s cubic-bezier(0.4,0,0.2,1);
    }}
    .bento-card:hover .bento-title::after {{ width: 100%; }}
    .bento-desc {{
        font-size: clamp(0.875rem,1.15vw,1rem) !important;
        line-height: 1.7 !important; opacity: 0.78 !important; margin: 0 !important;
    }}
    .bento-desc strong {{ color: var(--p); font-weight: 800; opacity: 1; }}
    .bento-card-line {{
        position: absolute; bottom: 0; left: 0; height: 3px; width: 0;
        background: linear-gradient(90deg, var(--p), var(--s));
        border-radius: 0 0 var(--radius) var(--radius);
        transition: width 0.5s cubic-bezier(0.4,0,0.2,1);
    }}
    .bento-card:hover .bento-card-line {{ width: 100%; }}
    .bento-grid > .bento-card:nth-child(4) .bento-num {{ color: rgba(255,255,255,0.25) !important; opacity: 1; }}
    .bento-grid > .bento-card:nth-child(4) .bento-tag {{ background: rgba(255,255,255,0.15); color: #fff; }}
    .bento-grid > .bento-card:nth-child(4) .bento-title {{ color: #fff !important; }}
    .bento-grid > .bento-card:nth-child(4) .bento-title::after {{ background: rgba(255,255,255,0.5); }}
    .bento-grid > .bento-card:nth-child(4) .bento-desc {{ color: rgba(255,255,255,0.85) !important; opacity: 1 !important; }}
    .bento-grid > .bento-card:nth-child(4) .bento-card-line {{ background: rgba(255,255,255,0.4); }}
"""


# ─────────────────────────────────────────────────────────────────────────────
# DARK MODE SYSTEM
# ─────────────────────────────────────────────────────────────────────────────

def _dark_mode_css(t: dict) -> str:
    dk_bg   = t.get("dk_bg",   "#0f0f0f")
    dk_card = t.get("dk_card", "#1a1a1a")
    dk_txt  = t.get("dk_txt",  "#e2e8f0")
    dk_nav  = t.get("dk_nav",  "rgba(15,15,15,0.9)")

    dm_vars = f"""
        --bg:      {dk_bg};
        --card:    {dk_card};
        --nav:     {dk_nav};
        --txt-h:   {dk_txt};
        --txt-b:   color-mix(in srgb, {dk_txt} 85%, transparent);
        --border:  1px solid rgba(255,255,255,0.08);
        --shadow:  0 8px 32px rgba(0,0,0,0.4);
        color-scheme: dark;"""

    return f"""
/* ── DARK MODE TRANSITIONS ─────────────────────────────── */
body, .card, .bento-card, nav#main-navbar, footer,
details, .pricing-wrapper, #cart-modal, #lead-popup,
#lang-modal, .contact-form input, .contact-form textarea,
.local-vault input, .filter-pill {{
    transition:
        background-color 0.4s ease,
        color            0.4s ease,
        border-color     0.35s ease,
        box-shadow       0.4s ease;
}}

/* ── JS CLASS TOGGLE ────────────────────────────────────── */
body.dark-mode {{
    {dm_vars}
    background: var(--bg);
    color: var(--txt-b);
}}
body.dark-mode nav#main-navbar {{ background: var(--nav); border-bottom-color: rgba(255,255,255,0.06); }}
body.dark-mode .card,
body.dark-mode .bento-card,
body.dark-mode .stats-ribbon,
body.dark-mode .pricing-wrapper,
body.dark-mode .detail-view,
body.dark-mode #cart-modal,
body.dark-mode #lead-popup,
body.dark-mode #lang-modal,
body.dark-mode details {{ background: var(--card); border-color: rgba(255,255,255,0.08); }}
body.dark-mode input,
body.dark-mode textarea,
body.dark-mode select,
body.dark-mode .local-vault input,
body.dark-mode .contact-form input,
body.dark-mode .contact-form textarea {{
    background:   var(--card);
    color:        var(--txt-h);
    border-color: rgba(255,255,255,0.1);
}}
body.dark-mode .filter-pill {{
    background:   var(--card);
    border-color: rgba(255,255,255,0.12);
    color:        var(--txt-h);
}}
body.dark-mode .filter-pill.active {{ background: var(--p); color: #fff; border-color: var(--p); }}
body.dark-mode img:not([src*=".svg"]) {{
    filter: brightness(0.88) contrast(1.05);
    transition: filter 0.4s ease;
}}
body.dark-mode #theme-toggle {{ background: var(--card); border-color: rgba(255,255,255,0.1); color: var(--txt-h); }}

/* ── OS PREFERENCE FALLBACK ─────────────────────────────── */
@media (prefers-color-scheme: dark) {{
    :root {{ {dm_vars} }}
    body {{ background: var(--bg); color: var(--txt-b); }}
    nav#main-navbar {{ background: var(--nav); }}
    .card, .bento-card {{ background: var(--card); border-color: rgba(255,255,255,0.08); }}
    img:not([src*=".svg"]) {{ filter: brightness(0.88) contrast(1.05); }}
    input, textarea, select {{ background: var(--card); color: var(--txt-h); border-color: rgba(255,255,255,0.1); }}
}}"""


# ─────────────────────────────────────────────────────────────────────────────
# MAIN CSS GENERATOR
# ─────────────────────────────────────────────────────────────────────────────

def generate_modern_css(
    theme_name: str,
    h_font: str,
    b_font: str,
    hero_align: str,
    h_color: str,
    b_color: str,
    h1_size: str,
    p_size: str,
    cta_bg: str,
    cta_txt: str,
) -> str:
    # ── 1. Theme lookup ─────────────────────────────────────────────────────
    t = THEME_REGISTRY.get(theme_name, THEME_REGISTRY["1. Stripe Cloud (Modern SaaS)"])

    # ── 2. Parse numeric values ──────────────────────────────────────────────
    try:
        h1_val = float(h1_size.replace("rem","").strip())
    except ValueError:
        h1_val = 4.5
    try:
        p_val = float(p_size.replace("rem","").strip())
    except ValueError:
        p_val = 1.1

    # ── 3. Fluid type scale ──────────────────────────────────────────────────
    scale   = _fluid_scale(h1_val)
    body_fs = _body_clamp(p_val)

    # ── 4. CLS suppression ───────────────────────────────────────────────────
    cls_block  = _cls_suppression_block(h_font, b_font)
    h_fallback = f"'{h_font} Fallback', " if h_font in [
        "Space Grotesk","Montserrat","Playfair Display","Outfit","Clash Display",
        "Inter","Plus Jakarta Sans","Satoshi","Roboto"
    ] else ""
    b_fallback = f"'{b_font} Fallback', " if b_font in [
        "Inter","Plus Jakarta Sans","Satoshi","Roboto"
    ] else ""

    # ── 5. CONTRAST SAFETY ───────────────────────────────────────────────────
    # Guarantee readable text on themed buttons regardless of user colour choice.
    # accessible_text_color() runs the WCAG 2.1 contrast ratio formula.
    safe_btn_on_primary = accessible_text_color(t['p'])
    safe_btn_on_accent  = accessible_text_color(t['s'])
    safe_cta_txt        = accessible_text_color(cta_bg, dark=h_color, light="#ffffff")

    # Derive hover colours programmatically — no hardcoded shades
    p_hover = darken_hex(t['p'] if not t['p'].startswith('rgba') and not t['p'].startswith('linear') else '#6366f1', 0.12)
    s_hover = darken_hex(t['s'] if not t['s'].startswith('rgba') and not t['s'].startswith('linear') else '#10b981', 0.12)
    p_alpha = alpha_hex(t['p'] if '#' in t['p'] else '#6366f1', 0.08)
    s_alpha = alpha_hex(t['s'] if '#' in t['s'] else '#10b981', 0.1)

    # ── 6. Theme-conditional effects ────────────────────────────────────────
    gradient_h1 = ""
    if any(x in theme_name for x in ["SaaS","Dark","Creative","Synthwave","Cyberpunk","Bold"]):
        gradient_h1 = (
            f"background: linear-gradient(135deg, {t['p']}, {t['s']});"
            " -webkit-background-clip: text; -webkit-text-fill-color: transparent;"
            " background-clip: text;"
        )

    btn_hover_rule = (
        "transform: translate(-4px,-4px); box-shadow: 8px 8px 0px #000;"
        if any(x in theme_name for x in ["Brutalist","Cyberpunk","Monochromatic"]) else
        "transform: translateY(-3px) scale(1.02); filter: brightness(1.1);"
        " box-shadow: 0 10px 25px -5px rgba(0,0,0,0.25);"
    )

    backdrop = (
        "backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px);"
        if any(x in theme_name for x in ["Glass","Mesh"]) else ""
    )

    # ── 7. Hero alignment ────────────────────────────────────────────────────
    if hero_align == "Left":
        h_align       = "text-align:left; justify-content:flex-start; align-items:center;"
        h_text_align  = "text-align:left;"
        h_text_items  = "align-items:flex-start;"
        h_btn_justify = "justify-content:flex-start;"
        hero_p_margin = "0 0 2.5rem 0"
        badge_align   = "flex-start"
    else:
        h_align       = "text-align:center; justify-content:center;"
        h_text_align  = "text-align:center;"
        h_text_items  = "align-items:center;"
        h_btn_justify = "justify-content:center;"
        hero_p_margin = "0 auto 2.5rem auto"
        badge_align   = "center"

    # ── 8. Sub-systems ───────────────────────────────────────────────────────
    bento_css = _bento_grid_css(theme_name, t["radius"])
    dark_css  = _dark_mode_css(t)

    # ── 9. Assemble ──────────────────────────────────────────────────────────
    return f"""
/* ════════════════════════════════════════════════════════════
   TITAN ENGINE v56  —  {theme_name}
   Generated CSS — do not edit manually.
   ════════════════════════════════════════════════════════════ */

/* ── CLS: METRIC-MATCHED FALLBACK FONTS ─────────────────── */
{cls_block}

/* ── CSS CUSTOM PROPERTIES ──────────────────────────────── */
:root {{
    /* Theme palette — all colour tokens participate in the transition system */
    --p:      {t['p']};
    --s:      {t['s']};
    --bg:     {t['bg']};
    --nav:    {t['nav']};
    --card:   {t['card']};
    --radius: {t['radius']};
    --shadow: {t['shadow']};
    --border: {t['border']};
    /* Smooth theme/dark-mode transitions applied universally */
    --transition-theme: background-color 0.45s cubic-bezier(0.4,0,0.2,1),
                        color            0.45s cubic-bezier(0.4,0,0.2,1),
                        border-color     0.35s cubic-bezier(0.4,0,0.2,1),
                        box-shadow       0.45s cubic-bezier(0.4,0,0.2,1),
                        fill             0.3s ease;

    /* Contrast-safe text on theme colours (WCAG AA auto-calculated) */
    --on-p:   {safe_btn_on_primary};
    --on-s:   {safe_btn_on_accent};
    --on-cta: {safe_cta_txt};

    /* Programmatic hover states */
    --p-hover: {p_hover};
    --s-hover: {s_hover};
    --p-alpha: {p_alpha};
    --s-alpha: {s_alpha};

    /* Typography stacks */
    --h-font: '{h_font}', {h_fallback}sans-serif;
    --b-font: '{b_font}', {b_fallback}sans-serif;

    /* User colour overrides */
    --txt-h:  {h_color};
    --txt-b:  {b_color};

    /* CTA */
    --cta-bg:  {cta_bg};
    --cta-txt: {safe_cta_txt};

    /* Fluid type scale */
    --fs-h1:   {scale['h1']};
    --fs-h2:   {scale['h2']};
    --fs-h3:   {scale['h3']};
    --fs-h4:   {scale['h4']};
    --fs-body: {body_fs};
    --fs-stat: {scale['stat']};

    /* Fluid spacing */
    --space-xs:  clamp(0.5rem,  1vw,  0.75rem);
    --space-sm:  clamp(0.75rem, 1.5vw, 1rem);
    --space-md:  clamp(1rem,    2vw,   1.5rem);
    --space-lg:  clamp(1.5rem,  3vw,   2.5rem);
    --space-xl:  clamp(2rem,    5vw,   4rem);
    --space-2xl: clamp(3rem,    8vw,   8rem);

    color-scheme: light dark;
}}

/* ── RESET ──────────────────────────────────────────────── */
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
html {{
    scroll-behavior: smooth;
    -webkit-text-size-adjust: 100%;
    text-size-adjust: 100%;
    scroll-padding-top: 80px; /* offset for fixed nav */
}}

/* ── BASE ───────────────────────────────────────────────── */
body {{
    background:     var(--bg);
    color:          var(--txt-b);
    font-family:    var(--b-font);
    font-size:      var(--fs-body);
    line-height:    1.8;
    letter-spacing: 0.01em;
    overflow-x:     hidden;
    width:          100%;
    max-width:      100vw;
    /* Universal smooth theme & dark-mode switching — covers bg, text, borders */
    transition: background-color 0.45s cubic-bezier(0.4,0,0.2,1),
                color            0.45s cubic-bezier(0.4,0,0.2,1);
}}
/* Apply colour transitions to all themed surfaces */
*, section, nav, footer, header, article, aside,
.card, .bento-card, .stats-ribbon, .pricing-wrapper,
#cart-modal, #lead-popup, #lang-modal, details,
input, textarea, select, button, a {{
    transition-property: background-color, color, border-color, box-shadow, fill;
    transition-duration: 0.4s;
    transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
}}
/* Restore fast/custom transitions for interactive elements — prevents sluggish hover */
.btn, .card, .bento-card, .nav-link, .social-link, .reveal,
.carousel-slide, .filter-pill, .lang-opt, .cart-close, details {{
    transition-duration: 0.3s !important;
}}
iframe, model-viewer {{ max-width: 100%; display: block; }}
img {{ display: block; max-width: 100%; }}

/* ── HEADINGS ───────────────────────────────────────────── */
h1, h2, h3, h4 {{
    font-family:    var(--h-font);
    color:          var(--txt-h);
    line-height:    1.1;
    font-weight:    800;
    margin-bottom:  var(--space-md);
    letter-spacing: -0.02em;
}}
h1 {{ font-size: var(--fs-h1); {gradient_h1} }}
h2 {{ font-size: var(--fs-h2); }}
h3 {{ font-size: var(--fs-h3); }}
h4 {{ font-size: var(--fs-h4); font-weight: 700; }}

p {{
    margin-bottom:  var(--space-md);
    opacity:        0.9;
    font-weight:    400;
    text-align:     justify;
    text-justify:   inter-word;
    hyphens:        auto;
    -webkit-hyphens: auto;
}}

/* ── LAYOUT ─────────────────────────────────────────────── */
.container {{
    max-width: 1300px;
    margin:    0 auto;
    padding:   0 clamp(1rem,4vw,2rem);
}}
main section {{ padding: var(--space-2xl) 0; position: relative; }}

/* Section heading system */
.section-head {{
    text-align:    center;
    margin-bottom: var(--space-xl);
}}
.section-head h2 {{ font-size: var(--fs-h2); margin-bottom: var(--space-sm); }}
.section-rule {{
    width:         60px;
    height:        4px;
    background:    linear-gradient(90deg, var(--p), var(--s));
    border-radius: 2px;
    margin:        0.75rem auto 0;
}}
.section-subtitle {{
    font-size:      clamp(0.85rem,1.2vw,1.1rem);
    color:          var(--txt-b);
    opacity:        0.7;
    text-transform: uppercase;
    letter-spacing: 2px;
    font-weight:    600;
    margin-top:     0.5rem;
}}

/* Grid systems */
.grid-3 {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(min(320px,100%), 1fr));
    gap: clamp(1rem,2.5vw,2.5rem);
}}
.about-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: clamp(2rem,5vw,5rem);
    align-items: center;
}}
.contact-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: clamp(2rem,4vw,4rem);
    align-items: stretch;
}}

/* ── CARD ───────────────────────────────────────────────── */
.card {{
    background:      var(--card);
    border-radius:   var(--radius);
    border:          var(--border);
    box-shadow:      var(--shadow);
    display:         flex;
    flex-direction:  column;
    overflow:        hidden;
    position:        relative;
    color:           var(--txt-b) !important;
    transition:
        transform    0.4s cubic-bezier(0.175,0.885,0.32,1.275),
        box-shadow   0.4s ease,
        border-color 0.35s ease,
        background-color 0.4s ease;
    /* Container context for @container queries */
    container-type: inline-size;
    container-name: card-cell;
    {backdrop}
}}
.card::before {{
    content:    '';
    position:   absolute;
    inset:      0 0 auto 0;
    height:     4px;
    background: linear-gradient(90deg, var(--p), var(--s));
    opacity:    0;
    transition: opacity 0.3s;
    z-index:    5;
}}
.card:hover {{ transform: translateY(-10px); box-shadow: 0 25px 50px -12px rgba(0,0,0,0.2); }}
.card:hover::before {{ opacity: 1; }}

/* Container query: narrow card layout */
@container card-cell (max-width: 280px) {{
    .card-body {{ padding: 1rem; }}
    .card h3 {{ font-size: 1rem !important; }}
}}

.card h3 {{
    font-size:      clamp(1.1rem,1.6vw,1.4rem) !important;
    font-weight:    800;
    line-height:    1.2;
    margin-bottom:  0.4rem;
    color:          var(--txt-h) !important;
    letter-spacing: -0.02em;
}}
.card-body {{
    padding:        clamp(1.25rem,2.5vw,2rem);
    display:        flex;
    flex-direction: column;
    flex-grow:      1;
}}
.card-desc {{
    font-size:           clamp(0.875rem,1.1vw,0.95rem);
    line-height:         1.6;
    opacity:             0.7;
    margin-bottom:       1.5rem;
    display:             -webkit-box;
    -webkit-line-clamp:  2;
    -webkit-box-orient:  vertical;
    overflow:            hidden;
    color:               var(--txt-b);
}}
.card-actions {{
    margin-top:  auto;
    display:     grid;
    grid-template-columns: 1fr 1fr;
    gap:         10px;
    padding-top: 15px;
}}
.prod-img {{
    width:       100%;
    height:      clamp(180px,20vw,280px);
    object-fit:  cover;
    transition:  transform 0.6s cubic-bezier(0.4,0,0.2,1);
}}
.card:hover .prod-img {{ transform: scale(1.08); }}
.prod-price {{
    font-weight:   700;
    color:         #059669;
    font-size:     clamp(1rem,1.3vw,1.2rem);
    margin-bottom: 10px;
}}

/* ── STORE FILTERS ──────────────────────────────────────── */
.store-filters {{
    display:         flex;
    flex-wrap:       wrap;
    gap:             0.5rem;
    justify-content: center;
    margin-bottom:   var(--space-lg);
}}
.filter-pill {{
    padding:         0.4rem 1.2rem;
    border-radius:   50px;
    border:          1px solid rgba(128,128,128,0.2);
    background:      var(--card);
    color:           var(--txt-b);
    font-size:       clamp(0.8rem,1vw,0.9rem);
    font-weight:     600;
    cursor:          pointer;
    transition:      all 0.25s ease;
    font-family:     var(--b-font);
}}
.filter-pill:hover {{ border-color: var(--p); color: var(--p); }}
.filter-pill.active {{
    background:   var(--p);
    border-color: var(--p);
    color:        var(--on-p);
    box-shadow:   0 4px 12px var(--p-alpha);
}}
.filter-pill:focus-visible {{
    outline:        3px solid var(--p);
    outline-offset: 2px;
}}

/* ── EMPTY STATE ────────────────────────────────────────── */
.empty-state {{
    text-align:  center;
    padding:     var(--space-2xl) 0;
    color:       var(--txt-b);
    opacity:     0.6;
    grid-column: 1 / -1;
}}
.error-msg {{
    color:       #ef4444;
    text-align:  center;
    padding:     var(--space-xl);
    grid-column: 1 / -1;
}}

/* ── BUTTONS ────────────────────────────────────────────── */
.btn {{
    display:         inline-flex;
    align-items:     center;
    justify-content: center;
    padding:         clamp(0.9rem,1.5vw,1.2rem) clamp(1.5rem,2.5vw,2.5rem);
    border-radius:   var(--radius);
    font-weight:     800;
    text-decoration: none;
    transition:      all 0.3s ease;
    text-transform:  uppercase;
    cursor:          pointer;
    border:          none;
    text-align:      center;
    font-size:       clamp(0.8rem,1vw,0.95rem);
    letter-spacing:  1.5px;
    position:        relative;
    overflow:        hidden;
    white-space:     nowrap;
    font-family:     var(--b-font);
}}
/* Ripple pseudo-element */
.btn::after {{
    content:       '';
    position:      absolute;
    inset:         50% 50% 50% 50%;
    background:    rgba(255,255,255,0.25);
    border-radius: 50%;
    transition:    inset 0.5s ease, opacity 0.5s ease;
    opacity:       0;
}}
.btn:active::after {{
    inset:   -20% -20% -20% -20%;
    opacity: 0;
    transition: inset 0s, opacity 0s;
}}
/* Contrast-safe: --on-p is auto-computed by accessible_text_color() */
.btn-primary {{ background: var(--p); color: var(--on-p) !important; }}
.btn-primary:hover {{ background: var(--p-hover); {btn_hover_rule} }}
.btn-accent  {{ background: var(--s); color: var(--on-s) !important; }}
.btn-accent:hover  {{ background: var(--s-hover); {btn_hover_rule} }}
.btn-cta     {{ background: var(--cta-bg); color: var(--cta-txt) !important; }}
.btn-outline-light {{
    background:   transparent;
    color:        var(--txt-h) !important;
    border:       2px solid currentColor;
}}
.btn-outline-light:hover {{ background: var(--txt-h); color: var(--bg) !important; }}
.btn:focus-visible {{ outline: 3px solid var(--p); outline-offset: 3px; }}
.btn:disabled {{ opacity: 0.5; cursor: not-allowed; pointer-events: none; }}

/* ── NAVIGATION ─────────────────────────────────────────── */
nav#main-navbar {{
    position:        fixed;
    top:             0;
    width:           100%;
    z-index:         2000;
    background:      var(--nav);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border-bottom:   1px solid rgba(128,128,128,0.1);
    padding:         clamp(0.8rem,1.5vw,1.2rem) 0;
    transition:      top 0.3s ease, background 0.4s ease, border-color 0.35s ease;
}}
.nav-flex  {{ display: flex; justify-content: space-between; align-items: center; }}
.nav-brand {{ display: flex; align-items: center; text-decoration: none; }}
.nav-wordmark {{
    font-family:    var(--h-font);
    font-weight:    900;
    font-size:      clamp(1.1rem,1.5vw,1.5rem);
    color:          var(--p);
    letter-spacing: -0.02em;
}}
.nav-links {{
    display:     flex;
    align-items: center;
    gap:         clamp(1rem,2vw,2rem);
}}
.nav-link {{
    text-decoration: none;
    font-weight:     600;
    color:           var(--txt-h);
    font-size:       clamp(0.85rem,1vw,0.95rem);
    transition:      color 0.2s;
    position:        relative;
    background:      none;
    border:          none;
    cursor:          pointer;
    font-family:     var(--b-font);
    padding:         0;
}}
/* Underline slide-in animation on nav links */
.nav-link::after {{
    content:          '';
    position:         absolute;
    width:            0;
    height:           2px;
    bottom:           -4px;
    left:             0;
    background:       var(--p);
    transition:       width 0.3s ease;
    border-radius:    1px;
}}
.nav-link:hover {{ color: var(--p); }}
.nav-link:hover::after {{ width: 100%; }}
.nav-link:focus-visible {{ outline: 2px solid var(--p); outline-offset: 4px; border-radius: 2px; }}

.nav-cta {{ margin-left: 0.5rem; }}

/* Hamburger icon */
.mobile-menu-btn {{
    display:    none;
    flex-direction: column;
    gap:        5px;
    background: none;
    border:     none;
    cursor:     pointer;
    padding:    6px;
    z-index:    2001;
}}
.hamburger-line {{
    display:          block;
    width:            24px;
    height:           2px;
    background:       var(--txt-h);
    border-radius:    2px;
    transition:       all 0.3s ease;
    transform-origin: center;
}}
/* Animate hamburger → ✕ */
.mobile-menu-btn.active .hamburger-line:nth-child(1) {{ transform: translateY(7px) rotate(45deg); }}
.mobile-menu-btn.active .hamburger-line:nth-child(2) {{ opacity: 0; transform: scaleX(0); }}
.mobile-menu-btn.active .hamburger-line:nth-child(3) {{ transform: translateY(-7px) rotate(-45deg); }}

/* ── HERO ───────────────────────────────────────────────── */
.hero {{
    position:    relative;
    min-height:  95vh;
    overflow:    hidden;
    display:     flex;
    {h_align}
    padding-top: clamp(80px,10vw,120px);
}}
.carousel-slide {{
    position:            absolute;
    inset:               0;
    background-size:     cover;
    background-position: center;
    opacity:             0;
    transition:          opacity 1.5s cubic-bezier(0.4,0,0.2,1),
                         transform 1.5s cubic-bezier(0.4,0,0.2,1);
    z-index:             0;
    transform:           scale(1.05);
}}
.carousel-slide.active {{ opacity: 1; transform: scale(1); }}

.modern-hero {{
    position:    relative;
    min-height:  100vh;
    display:     flex;
    {h_align}
    padding-top: clamp(80px,10vw,120px);
}}
.modern-hero-bg {{
    position:   absolute;
    top:        -50%;
    left:       -50%;
    width:      200%;
    height:     200%;
    background: radial-gradient(circle at 50% 50%, var(--p-alpha) 0%, transparent 50%);
    z-index:    -1;
    animation:  hero-bg-rotate 60s linear infinite;
}}
@keyframes hero-bg-rotate {{ to {{ transform: rotate(360deg); }} }}

.modern-hero-grid {{
    display:               grid;
    grid-template-columns: 1.1fr 1fr;
    gap:                   clamp(2rem,4vw,4rem);
    align-items:           center;
    width:                 100%;
}}
.modern-hero-text {{
    display:        flex;
    flex-direction: column;
    {h_text_align}
    {h_text_items}
}}
.hero-badge {{
    display:        inline-flex;
    align-items:    center;
    padding:        0.4rem 1rem;
    background:     var(--p-alpha);
    border:         1px solid rgba(128,128,128,0.2);
    border-radius:  50px;
    font-size:      clamp(0.75rem,1vw,0.9rem);
    font-weight:    700;
    margin-bottom:  var(--space-md);
    color:          var(--txt-h);
    text-transform: uppercase;
    letter-spacing: 1px;
    align-self:     {badge_align};
}}
.hero-sub {{
    font-size:   clamp(1rem,2vw,1.4rem);
    max-width:   700px;
    margin:      {hero_p_margin};
    opacity:     0.85;
    line-height: 1.65;
    font-weight: 400;
    color:       var(--txt-b);
}}
.hero-btn-group {{
    display:         flex;
    gap:             var(--space-sm);
    flex-wrap:       wrap;
    {h_btn_justify}
}}
.modern-hero-visual {{
    position:        relative;
    width:           100%;
    height:          clamp(300px,45vw,600px);
    display:         flex;
    align-items:     center;
    justify-content: center;
}}
.visual-frame {{
    width:         100%;
    height:        100%;
    border-radius: 32px;
    overflow:      hidden;
    position:      relative;
    z-index:       2;
    box-shadow:    0 30px 60px rgba(0,0,0,0.15);
    border:        8px solid var(--card);
}}
.hero-video-bg {{
    width:         100%;
    height:        100%;
    object-fit:    cover;
    pointer-events: none;
}}
.floating-element {{
    position:      absolute;
    border-radius: 50%;
    filter:        blur(60px);
    z-index:       1;
    opacity:       0.55;
    animation:     float-pulse 8s ease-in-out infinite alternate;
}}
@keyframes float-pulse {{
    from {{ transform: scale(1);    opacity: 0.55; }}
    to   {{ transform: scale(1.15); opacity: 0.35; }}
}}
.glow-1 {{ width:clamp(150px,25vw,300px); height:clamp(150px,25vw,300px); background:var(--p); top:-50px; right:-50px; animation-delay:0s; }}
.glow-2 {{ width:clamp(120px,20vw,250px); height:clamp(120px,20vw,250px); background:var(--s); bottom:-50px; left:-50px; animation-delay:-4s; }}

/* ── STATS RIBBON ───────────────────────────────────────── */
.stats-ribbon-container {{
    margin-top: clamp(-30px,-4vw,-60px);
    position:   relative;
    z-index:    100;
    padding:    0 clamp(0.5rem,2vw,20px);
}}
.stats-ribbon {{
    background:      var(--card);
    border-radius:   24px;
    padding:         clamp(1.5rem,3vw,3rem);
    display:         flex;
    justify-content: space-around;
    align-items:     center;
    box-shadow:      var(--shadow);
    border:          var(--border);
    backdrop-filter: blur(20px);
}}
.stat-block  {{ text-align: center; }}
.stat-number {{
    font-size:      var(--fs-stat);
    color:          var(--p);
    margin-bottom:  0.5rem;
    line-height:    1;
    font-family:    var(--h-font);
    font-weight:    900;
    letter-spacing: -0.03em;
}}
.stat-label {{
    font-size:      clamp(0.8rem,1.1vw,1.1rem);
    font-weight:    600;
    color:          var(--txt-b);
    text-transform: uppercase;
    letter-spacing: 1px;
    opacity:        0.8;
    margin:         0;
}}
.stat-divider {{ width:2px; height:60px; background:rgba(128,128,128,0.2); }}

/* ── PRICING TABLE ──────────────────────────────────────── */
.pricing-wrapper {{
    overflow-x:   auto;
    -webkit-overflow-scrolling: touch;
    box-shadow:   var(--shadow);
    border-radius: var(--radius);
    background:   var(--card);
    border:       var(--border);
}}
.pricing-table {{
    width:           100%;
    border-collapse: collapse;
    min-width:       560px;
}}
.pricing-table th {{
    background:     var(--p);
    color:          var(--on-p);
    padding:        clamp(1rem,2vw,2rem);
    text-align:     left;
    font-size:      clamp(0.85rem,1.1vw,1.05rem);
    text-transform: uppercase;
    letter-spacing: 1px;
    font-family:    var(--h-font);
}}
.titan-col {{ background: var(--s) !important; color: var(--on-s) !important; }}
.pricing-table td {{
    padding:       clamp(1rem,2vw,2rem);
    border-bottom: 1px solid rgba(128,128,128,0.1);
    color:         var(--txt-b);
    font-size:     clamp(0.85rem,1.1vw,1.05rem);
}}
.pricing-table tr:hover td {{ background: var(--p-alpha); }}
.savings-highlight {{ color: #059669; font-weight: 900; font-size: 1.1em; }}
.savings-row td, .savings-row th {{ background: var(--s-alpha); }}
.savings-cell {{ font-size: 1.05rem !important; color: var(--txt-h) !important; }}
.savings-cell strong {{ color: #059669; font-size: 1.2em; }}
.price-note {{ font-size: 0.75em; opacity: 0.6; font-weight: 400; }}

/* ── ABOUT ──────────────────────────────────────────────── */
.modern-about     {{ background: rgba(128,128,128,0.02); overflow: hidden; }}
.about-main-img   {{
    width:         100%;
    height:        clamp(300px,40vw,600px);
    object-fit:    cover;
    border-radius: 32px;
    box-shadow:    var(--shadow);
}}
.about-experience-badge {{
    position:      absolute;
    bottom:        clamp(-15px,-2vw,-30px);
    right:         clamp(-15px,-2vw,-30px);
    background:    var(--p);
    color:         var(--on-p);
    padding:       clamp(1rem,2vw,2rem);
    border-radius: 24px;
    box-shadow:    0 20px 40px rgba(0,0,0,0.2);
    display:       flex;
    align-items:   center;
    gap:           1rem;
    border:        4px solid var(--card);
}}
.about-experience-badge strong {{
    font-size:  clamp(2rem,3vw,3rem);
    line-height: 1;
    color:       var(--on-p);
}}
.about-experience-badge span {{
    font-size:      clamp(0.8rem,1vw,1rem);
    font-weight:    700;
    text-transform: uppercase;
    line-height:    1.2;
    color:          var(--on-p);
}}
.about-lead {{
    font-size:    clamp(1rem,1.5vw,1.25rem);
    line-height:  1.8;
    opacity:      0.9;
    color:        var(--txt-b);
    border-left:  4px solid var(--s);
    padding-left: clamp(1rem,2vw,1.5rem);
}}
.about-visual {{ position: relative; }}

/* ── TESTIMONIALS ───────────────────────────────────────── */
.testi-quote-mark {{ color: var(--p); opacity: 0.35; margin-bottom: 1rem; }}
.testi-quote {{ flex-grow: 1; }}
.testi-quote p {{
    font-size:     clamp(0.95rem,1.3vw,1.1rem);
    font-style:    italic;
    line-height:   1.75;
    opacity:       0.9;
    margin-bottom: 1.5rem;
    color:         var(--txt-b);
}}
.testi-author {{
    display:         flex;
    align-items:     center;
    gap:             15px;
    border-top:      1px solid rgba(128,128,128,0.1);
    padding-top:     1.25rem;
}}
.testi-avatar {{
    width:           44px;
    height:          44px;
    min-width:       44px;
    border-radius:   50%;
    background:      var(--p);
    color:           var(--on-p);
    display:         flex;
    align-items:     center;
    justify-content: center;
    font-weight:     800;
    font-size:       1.2rem;
    flex-shrink:     0;
}}
.testi-name  {{ display: block; font-weight: 700; color: var(--txt-h); font-size: 1rem; }}
.testi-role  {{ display: block; font-size: 0.8rem; opacity: 0.55; margin-top: 2px; }}

/* ── FAQ ────────────────────────────────────────────────── */
details {{
    background:    var(--card);
    border:        var(--border);
    border-radius: var(--radius);
    margin-bottom: var(--space-sm);
    padding:       var(--space-md);
    cursor:        pointer;
    transition:    box-shadow 0.3s, transform 0.3s, background-color 0.4s;
}}
details:hover {{ box-shadow: var(--shadow); transform: translateX(5px); border-left: 4px solid var(--p); }}
details[open] {{ border-left: 4px solid var(--s); }}
details summary {{
    font-weight: 800;
    font-size:   clamp(1rem,1.4vw,1.2rem);
    outline:     none;
    list-style:  none;
    color:       var(--txt-h);
}}
details summary::-webkit-details-marker {{ display: none; }}
details p {{ margin-top: 1rem; margin-bottom: 0; opacity: 0.85; }}

/* ── CTA BAND ───────────────────────────────────────────── */
.cta-band {{
    background: linear-gradient(135deg, var(--p), var(--s));
    color:      var(--on-p);
    text-align: center;
    padding:    var(--space-2xl) 0;
}}
.cta-band h2 {{ color: var(--on-p) !important; -webkit-text-fill-color: var(--on-p); background: none; margin-bottom: 1rem; }}
.cta-band p  {{ color: var(--on-p) !important; opacity: 0.9; margin-bottom: 2rem; }}
.cta-band-btn {{
    background:    rgba(255,255,255,0.15);
    color:         #fff !important;
    border:        2px solid rgba(255,255,255,0.5);
    backdrop-filter: blur(8px);
    padding:       1.2rem 3rem;
    font-size:     clamp(0.9rem,1.2vw,1.1rem);
}}
.cta-band-btn:hover {{
    background: rgba(255,255,255,0.25);
    border-color: rgba(255,255,255,0.8);
    transform: translateY(-3px);
}}

/* ── FOOTER ─────────────────────────────────────────────── */
footer {{
    background: #0f172a;
    color:      #f8fafc;
    padding:    clamp(3rem,6vw,6rem) 0 clamp(2rem,3vw,3rem) 0;
    margin-top: auto;
    border-top: 4px solid var(--p);
}}
.footer-grid {{
    display:               grid;
    grid-template-columns: repeat(auto-fit, minmax(min(220px,100%), 1fr));
    gap:                   clamp(2rem,4vw,4rem);
    margin-bottom:         var(--space-xl);
}}
.footer-brand h3  {{ color: #fff; font-size: clamp(1.2rem,1.8vw,1.6rem); margin-bottom: 0.5rem; }}
.footer-tagline   {{ color: rgba(255,255,255,0.5); font-size: 0.9rem; margin-bottom: 1rem; }}
.footer-address   {{ color: rgba(255,255,255,0.6); font-size: 0.9rem; line-height: 1.6; margin-bottom: 1.5rem; }}
.social-links     {{ display: flex; flex-wrap: wrap; gap: 12px; }}
.social-link      {{
    display:         flex;
    align-items:     center;
    justify-content: center;
    width:           40px;
    height:          40px;
    border-radius:   50%;
    background:      rgba(255,255,255,0.06);
    transition:      background 0.3s, transform 0.3s;
    text-decoration: none;
}}
.social-link:hover {{ background: var(--brand, var(--p)); transform: translateY(-3px) scale(1.1); box-shadow: 0 8px 20px color-mix(in srgb, var(--brand, var(--p)) 40%, transparent); }}
.social-icon {{ width: 20px; height: 20px; fill: rgba(255,255,255,0.75); transition: fill 0.25s; }}
.social-link:hover .social-icon {{ fill: #ffffff; }}
/* Brand colour per platform (set via style="--brand:#hex" on each anchor) */
.social-link--instagram {{ background: rgba(255,255,255,0.06); }}
.social-link--instagram:hover {{ background: linear-gradient(45deg,#f09433,#e6683c,#dc2743,#cc2366,#bc1888) !important; }}
.social-link--instagram:hover .social-icon {{ fill: #fff; }}
.footer-nav h4 {{
    color:          rgba(255,255,255,0.5);
    font-size:      0.75rem;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-bottom:  1.25rem;
}}
.footer-nav a {{
    color:           rgba(255,255,255,0.65) !important;
    text-decoration: none;
    display:         block;
    margin-bottom:   0.85rem;
    font-size:       clamp(0.9rem,1.1vw,1rem);
    transition:      color 0.25s, transform 0.25s;
}}
.footer-nav a:hover {{ color: #fff !important; transform: translateX(5px); }}
.footer-bottom {{
    border-top:  1px solid rgba(255,255,255,0.1);
    padding-top: 2rem;
    text-align:  center;
    color:       rgba(255,255,255,0.4);
    font-size:   0.9rem;
}}
.footer-bottom span {{ color: rgba(255,255,255,0.65); }}

/* ── CART SYSTEM ────────────────────────────────────────── */
#cart-float {{
    position:      fixed;
    bottom:        100px;
    right:         30px;
    background:    var(--p);
    color:         var(--on-p);
    padding:       15px 25px;
    border-radius: 50px;
    box-shadow:    0 10px 25px rgba(0,0,0,0.3);
    cursor:        pointer;
    z-index:       1000;
    display:       flex;
    align-items:   center;
    gap:           10px;
    font-weight:   800;
    transition:    transform 0.3s, box-shadow 0.3s;
    border:        none;
    font-family:   var(--b-font);
    font-size:     1rem;
}}
#cart-float:hover {{ transform: scale(1.05) translateY(-5px); box-shadow: 0 15px 35px rgba(0,0,0,0.4); }}

#cart-overlay {{
    display:         none;
    position:        fixed;
    inset:           0;
    background:      rgba(0,0,0,0.7);
    backdrop-filter: blur(5px);
    z-index:         3000;
}}

#cart-modal {{
    position:      fixed;
    top:           50%;
    left:          50%;
    transform:     translate(-50%, calc(-50% + 30px));
    background:    var(--card);
    width:         90%;
    max-width:     480px;
    max-height:    88vh;
    overflow-y:    auto;
    padding:       clamp(1.5rem,3vw,2.5rem);
    border-radius: 24px;
    box-shadow:    0 30px 60px rgba(0,0,0,0.4);
    z-index:       3001;
    border:        var(--border);
    color:         var(--txt-b);
    opacity:       0;
    pointer-events: none;
    transition:    transform 0.4s cubic-bezier(0.175,0.885,0.32,1.275),
                   opacity   0.35s ease;
    will-change:   transform, opacity;
}}
#cart-modal.open {{
    transform:      translate(-50%, -50%);
    opacity:        1;
    pointer-events: all;
}}
.cart-close {{
    position:    absolute;
    top:         16px;
    right:       20px;
    background:  none;
    border:      none;
    cursor:      pointer;
    font-size:   1.75rem;
    color:       var(--txt-b);
    line-height: 1;
    transition:  color 0.2s, transform 0.2s;
    padding:     4px 8px;
    border-radius: 50%;
}}
.cart-close:hover {{ color: var(--p); transform: rotate(90deg); }}
#cart-modal h3 {{
    color:          var(--p);
    font-size:      clamp(1.3rem,2vw,1.8rem);
    border-bottom:  1px solid rgba(128,128,128,0.1);
    padding-bottom: 1rem;
    margin-bottom:  1.5rem;
    padding-right:  40px; /* clear close btn */
}}
.cart-item {{
    display:       flex;
    align-items:   center;
    border-bottom: 1px solid rgba(128,128,128,0.1);
    padding:       12px 0;
    gap:           12px;
    font-size:     clamp(0.85rem,1.1vw,1rem);
}}
.cart-item-name {{ flex: 1; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
.cart-item-controls {{
    display:     flex;
    align-items: center;
    gap:         8px;
    flex-shrink: 0;
}}
.cart-item-controls button {{
    width:        28px;
    height:       28px;
    border-radius: 50%;
    border:       1px solid rgba(128,128,128,0.2);
    background:   var(--bg);
    color:        var(--txt-h);
    cursor:       pointer;
    font-size:    1rem;
    display:      flex;
    align-items:  center;
    justify-content: center;
    transition:   background 0.2s;
    font-family:  var(--b-font);
}}
.cart-item-controls button:hover {{ background: var(--p); color: var(--on-p); border-color: var(--p); }}
.cart-qty {{ font-weight: 700; min-width: 20px; text-align: center; color: var(--txt-h); }}
.cart-item-price {{ font-weight: 700; color: #059669; white-space: nowrap; }}
.cart-remove {{
    width:       24px !important;
    height:      24px !important;
    color:       #ef4444 !important;
    border-color: rgba(239,68,68,0.3) !important;
    font-size:   0.9rem !important;
}}
.cart-remove:hover {{ background: #ef4444 !important; color: #fff !important; }}
.cart-total-row {{
    display:       flex;
    justify-content: space-between;
    align-items:   center;
    font-size:     clamp(1rem,1.5vw,1.2rem);
    padding:       1rem 0;
    margin-top:    0.5rem;
    border-top:    2px solid rgba(128,128,128,0.1);
}}
.cart-total-row strong {{ font-size: 1.3em; color: var(--p); }}
.local-vault {{
    background:    var(--p-alpha);
    padding:       var(--space-md);
    border-radius: 12px;
    margin-top:    var(--space-md);
    border:        1px solid rgba(128,128,128,0.1);
}}
.vault-label {{ font-size: 0.85rem; font-weight: 700; margin-bottom: 0.75rem; color: var(--txt-h); }}
.local-vault input {{
    width:         100%;
    padding:       0.9rem 1rem;
    margin-top:    0.5rem;
    border-radius: 8px;
    border:        1px solid rgba(128,128,128,0.2);
    background:    var(--bg);
    color:         var(--txt-b);
    font-size:     1rem;
    font-family:   var(--b-font);
    transition:    border-color 0.2s, box-shadow 0.2s;
}}
.local-vault input:focus {{
    outline:      none;
    border-color: var(--p);
    box-shadow:   0 0 0 3px var(--p-alpha);
}}

/* ── WHATSAPP WIDGET ────────────────────────────────────── */
.wa-float-btn {{
    position:        fixed;
    bottom:          30px;
    right:           30px;
    background:      #25D366;
    width:           60px;
    height:          60px;
    border-radius:   50%;
    display:         flex;
    align-items:     center;
    justify-content: center;
    box-shadow:      0 4px 20px rgba(37,211,102,0.4);
    z-index:         999;
    transition:      transform 0.3s, box-shadow 0.3s;
    text-decoration: none;
    overflow:        hidden;
}}
.wa-label {{
    position: absolute;
    right:    70px;
    background: #25D366;
    color:    #fff;
    padding:  0.35rem 0.75rem;
    border-radius: 50px;
    font-size: 0.85rem;
    font-weight: 700;
    white-space: nowrap;
    opacity:  0;
    transform: translateX(10px);
    transition: all 0.3s ease;
    pointer-events: none;
}}
.wa-float-btn:hover {{ transform: scale(1.12); box-shadow: 0 8px 28px rgba(37,211,102,0.55); }}
.wa-float-btn:hover .wa-label {{ opacity: 1; transform: translateX(0); }}

/* ── LEAD POPUP ─────────────────────────────────────────── */
#popup-overlay {{
    position:        fixed;
    inset:           0;
    background:      rgba(0,0,0,0.65);
    backdrop-filter: blur(4px);
    z-index:         3000;
}}
#lead-popup {{
    position:      fixed;
    top:           50%;
    left:          50%;
    transform:     translate(-50%,-50%);
    background:    var(--card);
    padding:       clamp(2rem,4vw,3.5rem);
    text-align:    center;
    border-radius: var(--radius);
    z-index:       3001;
    box-shadow:    0 30px 60px rgba(0,0,0,0.5);
    width:         90%;
    max-width:     480px;
    border:        var(--border);
    animation:     popup-in 0.5s cubic-bezier(0.175,0.885,0.32,1.275) both;
}}
@keyframes popup-in {{
    from {{ transform: translate(-50%,-50%) scale(0.85); opacity: 0; }}
    to   {{ transform: translate(-50%,-50%) scale(1);    opacity: 1; }}
}}
.popup-icon   {{ font-size: 3rem; margin-bottom: 1rem; line-height: 1; }}
#lead-popup h3 {{ color: var(--p); margin-bottom: 0.75rem; }}
#lead-popup p  {{ opacity: 0.8; margin-bottom: 1.5rem; }}
.close-popup {{
    position:     absolute;
    top:          15px;
    right:        20px;
    cursor:       pointer;
    font-size:    2rem;
    opacity:      0.4;
    transition:   opacity 0.2s, color 0.2s;
    background:   none;
    border:       none;
    color:        var(--txt-h);
    line-height:  1;
    padding:      4px 8px;
}}
.close-popup:hover {{ opacity: 1; color: var(--p); }}
.popup-cta-btn {{ width: 100%; }}

/* ── LANGUAGE MODAL ─────────────────────────────────────── */
#lang-modal {{
    position:      fixed;
    top:           50%;
    left:          50%;
    transform:     translate(-50%,-50%);
    background:    var(--card);
    width:         90%;
    max-width:     480px;
    padding:       clamp(1.5rem,3vw,3rem);
    border-radius: 24px;
    box-shadow:    0 30px 60px rgba(0,0,0,0.4);
    z-index:       3001;
    border:        var(--border);
}}
#lang-modal h3 {{
    text-align:     center;
    color:          var(--p);
    font-size:      clamp(1.3rem,2vw,1.8rem);
    border-bottom:  1px solid rgba(128,128,128,0.1);
    padding-bottom: 1rem;
    margin-bottom:  1.5rem;
}}
.lang-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }}
.lang-opt {{
    display:         flex;
    align-items:     center;
    justify-content: center;
    padding:         1.1rem;
    border:          var(--border);
    border-radius:   12px;
    cursor:          pointer;
    font-weight:     600;
    font-size:       0.95rem;
    transition:      all 0.25s ease;
    background:      var(--bg);
    color:           var(--txt-h);
    font-family:     var(--b-font);
    gap:             8px;
}}
.lang-opt:hover {{ background: var(--p); color: var(--on-p); transform: translateY(-3px); box-shadow: 0 8px 20px var(--p-alpha); }}
.lang-opt:focus-visible {{ outline: 3px solid var(--p); outline-offset: 2px; }}

/* ── TOP PROMO BAR ──────────────────────────────────────── */
#top-bar {{
    position:       fixed;
    top:            0;
    left:           0;
    width:          100%;
    background:     var(--s);
    color:          var(--on-s);
    text-align:     center;
    padding:        clamp(8px,1vw,12px) 3rem;
    z-index:        2005;
    font-weight:    700;
    font-size:      clamp(0.8rem,1vw,0.9rem);
    letter-spacing: 0.5px;
    display:        flex;
    align-items:    center;
    justify-content: center;
    gap:            1rem;
}}
#top-bar a {{ color: var(--on-s) !important; text-decoration: underline; }}
.top-bar-close {{
    position:   absolute;
    right:      12px;
    top:        50%;
    transform:  translateY(-50%);
    background: none;
    border:     none;
    color:      var(--on-s);
    cursor:     pointer;
    font-size:  1.2rem;
    opacity:    0.6;
    transition: opacity 0.2s;
}}
.top-bar-close:hover {{ opacity: 1; }}

/* ── DARK MODE TOGGLE ───────────────────────────────────── */
#theme-toggle {{
    position:        fixed;
    bottom:          30px;
    left:            30px;
    width:           48px;
    height:          48px;
    background:      var(--card);
    border-radius:   50%;
    display:         flex;
    align-items:     center;
    justify-content: center;
    box-shadow:      0 8px 20px rgba(0,0,0,0.15);
    cursor:          pointer;
    z-index:         1000;
    font-size:       1.4rem;
    border:          var(--border);
    transition:      transform 0.3s, border-color 0.3s, background-color 0.4s;
}}
#theme-toggle:hover {{ transform: scale(1.1) rotate(15deg); border-color: var(--p); }}
#theme-toggle:focus-visible {{ outline: 3px solid var(--p); outline-offset: 3px; }}

/* ── VOICE SEARCH BTN ───────────────────────────────────── */
.voice-search-btn {{
    background:   none;
    border:       1px solid rgba(128,128,128,0.25);
    border-radius: 50px;
    padding:      0.4rem 1rem;
    color:        var(--txt-b);
    cursor:       pointer;
    font-size:    0.875rem;
    font-family:  var(--b-font);
    font-weight:  600;
    transition:   all 0.25s ease;
    margin-top:   0.5rem;
}}
.voice-search-btn:hover {{ border-color: var(--p); color: var(--p); background: var(--p-alpha); }}

.listening {{ animation: voice-pulse 1.5s infinite; background: var(--s-alpha) !important; border-color: var(--s) !important; color: var(--s) !important; }}
@keyframes voice-pulse {{
    0%,100% {{ box-shadow: 0 0 0 0 rgba(0,0,0,0); }}
    50%      {{ box-shadow: 0 0 0 12px rgba(0,0,0,0); }}
}}

/* ── CONTACT PAGE ───────────────────────────────────────── */
.contact-section {{ background: var(--bg); }}
.contact-info-card,
.contact-form-card {{
    padding: clamp(1.5rem,4vw,3rem);
}}
.contact-info-card h3,
.contact-form-card h3 {{
    color:         var(--p);
    margin-bottom: 1.5rem;
    font-size:     clamp(1.3rem,2vw,1.8rem);
}}
.contact-detail {{ margin-bottom: 1.25rem; }}
.contact-label {{
    display:       block;
    font-size:     0.75rem;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    font-weight:   700;
    color:         var(--p);
    margin-bottom: 0.3rem;
    opacity:       0.8;
}}
.contact-link {{ color: var(--txt-h) !important; font-weight: 600; text-decoration: none; transition: color 0.2s; }}
.contact-link:hover {{ color: var(--p) !important; }}
.wa-contact-btn {{ width: 100%; margin-top: 1.5rem; }}

/* Contact form */
.contact-form {{ display: flex; flex-direction: column; gap: 1.25rem; }}
.form-group {{ display: flex; flex-direction: column; gap: 0.4rem; }}
.form-group label {{
    font-size:   0.85rem;
    font-weight: 700;
    color:       var(--txt-h);
    opacity:     0.8;
}}
.contact-form input,
.contact-form textarea {{
    width:         100%;
    padding:       1rem 1.1rem;
    border:        1px solid rgba(128,128,128,0.2);
    border-radius: 10px;
    background:    var(--bg);
    color:         var(--txt-b);
    font-size:     1rem;
    font-family:   var(--b-font);
    transition:    border-color 0.25s, box-shadow 0.25s;
    resize:        vertical;
}}
.contact-form input:focus,
.contact-form textarea:focus {{
    outline:      none;
    border-color: var(--p);
    box-shadow:   0 0 0 4px var(--p-alpha);
}}
.contact-form input::placeholder,
.contact-form textarea::placeholder {{ opacity: 0.45; }}
.map-container {{
    border-radius: var(--radius);
    overflow:      hidden;
    border:        var(--border);
    margin-top:    var(--space-xl);
    height:        420px;
    position:      relative;
}}
.map-container iframe {{ width: 100%; height: 100%; border: none; }}

/* ── INNER PAGE HEADER ──────────────────────────────────── */
.inner-page-header {{
    background:       linear-gradient(135deg, var(--p), var(--s));
    display:          flex;
    align-items:      center;
    justify-content:  center;
    text-align:       center;
    padding:          clamp(100px,12vw,160px) 1rem clamp(3rem,5vw,5rem);
    position:         relative;
    overflow:         hidden;
}}
.inner-page-header::after {{
    content:    '';
    position:   absolute;
    inset:      0;
    background: radial-gradient(circle at 70% 40%, rgba(255,255,255,0.08) 0%, transparent 60%);
}}
.inner-page-header h1 {{
    color:   #fff !important;
    -webkit-text-fill-color: #fff !important;
    background: none;
    position: relative;
    z-index:  2;
    font-size: clamp(2.5rem,5vw,4rem);
}}
.inner-page-header p {{ color: rgba(255,255,255,0.85) !important; position: relative; z-index: 2; }}
.inner-body-section {{ background: var(--bg); }}
.inner-body {{ max-width: 860px; margin: 0 auto; padding-top: var(--space-2xl); padding-bottom: var(--space-2xl); }}
.inner-body p, .inner-body li {{ line-height: 1.85; opacity: 0.9; }}

/* ── PRODUCT DETAIL ─────────────────────────────────────── */
.product-section {{ padding-top: clamp(100px,12vw,140px); background: var(--bg); min-height: 100vh; }}
.detail-view {{
    display:               grid;
    grid-template-columns: 0.85fr 1.15fr;
    gap:                   clamp(2rem,5vw,6rem);
    align-items:           start;
    background:            var(--card);
    padding:               clamp(1.5rem,4vw,5rem);
    border-radius:         32px;
    box-shadow:            var(--shadow);
    border:                var(--border);
}}
.product-media-column {{ position: sticky; top: 130px; }}
.product-info-column h1 {{ font-size: clamp(1.8rem,3vw,2.8rem) !important; margin-bottom: var(--space-sm) !important; }}
.product-price-tag {{
    display:       inline-block;
    padding:       0.5rem 1.5rem;
    background:    rgba(5,150,105,0.1);
    color:         #059669;
    font-size:     clamp(1.2rem,2vw,1.8rem);
    font-weight:   900;
    border-radius: 50px;
    margin-bottom: var(--space-md);
}}
.product-specs-container, .product-specs-container p {{ font-size: clamp(0.9rem,1.2vw,1.05rem) !important; line-height: 1.7 !important; }}
.product-specs-container strong {{ display: block; margin-top: var(--space-md); font-size: clamp(1rem,1.4vw,1.1rem); color: var(--p); }}
.prod-actions {{ margin-top: var(--space-lg); }}
.prod-action-btn {{ min-width: 240px; height: 4rem; }}
.gallery-thumbs {{ display: flex; gap: 12px; margin-top: 16px; overflow-x: auto; padding-bottom: 8px; }}
.thumb {{
    width:         70px;
    height:        70px;
    flex-shrink:   0;
    border-radius: var(--radius);
    object-fit:    cover;
    cursor:        pointer;
    border:        2px solid transparent;
    opacity:       0.65;
    transition:    all 0.25s;
}}
.thumb:hover, .thumb.active {{ border-color: var(--p); opacity: 1; transform: translateY(-4px); }}
.thumb-3d {{
    display:         flex;
    align-items:     center;
    justify-content: center;
    background:      var(--p-alpha);
    border:          2px solid var(--p) !important;
    color:           var(--p);
    font-size:       0.75rem;
    font-weight:     700;
    font-family:     var(--b-font);
    cursor:          pointer;
    opacity:         1 !important;
}}
.back-btn {{
    display:         inline-flex;
    align-items:     center;
    gap:             6px;
    font-size:       clamp(0.8rem,1vw,0.9rem);
    font-weight:     700;
    color:           var(--p) !important;
    text-decoration: none;
    margin-bottom:   clamp(16px,2vw,28px);
    text-transform:  uppercase;
    letter-spacing:  1px;
    transition:      gap 0.2s;
}}
.back-btn:hover {{ gap: 10px; }}

/* ── BLOG ───────────────────────────────────────────────── */
.blog-hero {{
    position:            relative;
    min-height:          40vh;
    background-size:     cover;
    background-position: center;
    display:             flex;
    align-items:         center;
    justify-content:     center;
    text-align:          center;
    padding:             clamp(100px,12vw,140px) 1rem 3rem;
}}
.blog-hero h1 {{ color: #fff !important; -webkit-text-fill-color: #fff !important; background: none; }}
.blog-hero p  {{ color: rgba(255,255,255,0.85) !important; }}
.blog-category {{
    display:        inline-block;
    background:     var(--p-alpha);
    color:          var(--p);
    padding:        0.25rem 0.75rem;
    border-radius:  50px;
    font-size:      0.75rem;
    font-weight:    700;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom:  0.75rem;
}}
.blog-title-link {{
    color:           var(--txt-h) !important;
    text-decoration: none;
    transition:      color 0.2s;
}}
.blog-title-link:hover {{ color: var(--p) !important; }}
.blog-read-btn {{ margin-top: auto; width: 100%; }}

/* Blog post */
.blog-post-container {{ background: var(--bg); }}
.post-header {{
    background:  linear-gradient(135deg, var(--p), var(--s));
    padding:     clamp(100px,12vw,140px) 1rem 3rem;
    text-align:  center;
}}
.post-header h1 {{ color: #fff !important; -webkit-text-fill-color: #fff !important; background: none; }}
.post-meta {{ color: rgba(255,255,255,0.7); font-size: 0.9rem; }}
.post-body {{ max-width: 800px; margin: 0 auto; padding: var(--space-2xl) 1rem; }}
.post-hero-img {{ width: 100%; border-radius: 16px; margin-bottom: var(--space-xl); box-shadow: var(--shadow); }}
.post-content p {{ line-height: 1.85; margin-bottom: 1.5rem; text-align: left; }}
.post-content h2, .post-content h3 {{ margin-top: 2rem; }}
.post-back-btn {{ margin-top: var(--space-xl); }}

/* ── BOOKING ────────────────────────────────────────────── */
.booking-section {{ background: var(--bg); }}
.booking-embed-wrapper {{
    background:    var(--card);
    border-radius: var(--radius);
    overflow:      hidden;
    box-shadow:    var(--shadow);
    border:        var(--border);
    max-width:     860px;
    margin:        0 auto;
}}

/* ── REVEAL / ANIMATION ─────────────────────────────────── */
.reveal {{
    opacity:    0;
    transform:  translateY(40px);
    transition: opacity  0.8s cubic-bezier(0.25,0.46,0.45,0.94),
                transform 0.8s cubic-bezier(0.25,0.46,0.45,0.94);
    position:   relative;
    z-index:    10;
}}
.reveal.active {{ opacity: 1; transform: translateY(0); }}

/* Stagger children when parent is .section-head */
.section-head.reveal.active > * {{ animation: none; }}

/* Respect reduced motion */
@media (prefers-reduced-motion: reduce) {{
    .reveal, .card, .bento-card, .carousel-slide, body,
    .modern-hero-bg, .floating-element, .wa-label {{
        transition: none !important;
        animation:  none !important;
    }}
    html {{ scroll-behavior: auto; }}
}}

/* ── BENTO GRID ─────────────────────────────────────────── */
{bento_css}

/* ── DARK MODE SYSTEM ───────────────────────────────────── */
{dark_css}

/* ════════════════════════════════════════════════════════════
   RESPONSIVE: TABLET (≤ 992px)
   ════════════════════════════════════════════════════════════ */
@media (max-width: 992px) {{
    nav#main-navbar .nav-links {{
        position:       absolute;
        top:            100%;
        left:           -100%;
        width:          100vw;
        height:         100dvh;
        background:     var(--bg);
        flex-direction: column;
        padding:        3rem;
        transition:     left 0.4s cubic-bezier(0.4,0,0.2,1);
        align-items:    center;
        justify-content: flex-start;
        gap:            2.5rem;
        z-index:        1999;
        overflow-y:     auto;
        overscroll-behavior: contain;
    }}
    nav#main-navbar .nav-links.active {{ left: 0; }}
    .nav-links .nav-link {{ font-size: 1.4rem; }}
    .mobile-menu-btn {{ display: flex; }}

    .about-grid,
    .detail-view,
    .grid-3,
    .contact-grid {{ grid-template-columns: 1fr !important; gap: 2rem; }}

    .modern-hero-grid {{ grid-template-columns: 1fr; text-align: center; }}
    .modern-hero-text {{ text-align: center; align-items: center; }}
    .hero-btn-group   {{ justify-content: center; }}
    .modern-hero-visual {{ height: clamp(260px,40vw,400px); }}

    .detail-view {{ padding: clamp(1.5rem,3vw,2rem); gap: 2rem; }}
    .product-media-column {{ position: relative; top: 0; margin-bottom: 2rem; }}

    .stats-ribbon {{ flex-direction: column; padding: 2.5rem 1.5rem; gap: 2rem; }}
    .stat-divider {{ width: 100%; height: 2px; }}
    .stats-ribbon-container {{ margin-top: -30px; }}

    .about-experience-badge {{
        position:     relative;
        bottom:       0; right: 0;
        margin:       -30px auto 0;
        width:        fit-content;
        z-index:      10;
    }}
}}

/* ════════════════════════════════════════════════════════════
   RESPONSIVE: MOBILE (≤ 480px)
   ════════════════════════════════════════════════════════════ */
@media (max-width: 480px) {{
    p {{ text-align: left; hyphens: auto; }}

    html, body {{
        width: 100% !important; margin: 0 !important;
        padding: 0 !important; overflow-x: hidden !important;
    }}
    .container {{ width: 100% !important; max-width: 100% !important; padding: 0 clamp(1rem,5vw,1.5rem) !important; }}

    footer {{ padding-bottom: 9rem !important; }}
    .footer-grid {{ display: flex !important; flex-direction: column !important; gap: 2.5rem !important; text-align: left !important; }}

    .hero-btn-group {{ flex-direction: column !important; width: 100%; }}
    .hero-btn-group .btn {{ width: 100% !important; }}

    /* Floating buttons: scale down, pin to safe corners */
    .wa-float-btn {{ bottom: 14px !important; right: 10px !important; width: 52px !important; height: 52px !important; }}
    .wa-label {{ display: none; }}
    #theme-toggle {{ bottom: 14px !important; left: 10px !important; width: 44px !important; height: 44px !important; }}
    #cart-float {{ bottom: 76px !important; right: 10px !important; scale: 0.85; }}

    .modern-hero-visual {{ height: 260px !important; margin-top: 1.5rem !important; }}
    .visual-frame {{ border-width: 4px !important; }}

    .detail-view {{ grid-template-columns: 1fr !important; }}
    .pricing-table {{ min-width: 100% !important; }}
    .pricing-table th, .pricing-table td {{ padding: 0.75rem 0.5rem !important; font-size: 0.85rem !important; }}

    .lang-grid {{ grid-template-columns: 1fr 1fr; }}

    .contact-grid {{ grid-template-columns: 1fr !important; }}

    /* Cart modal full-height on mobile */
    #cart-modal {{
        width:         100% !important;
        max-width:     100% !important;
        border-radius: 24px 24px 0 0 !important;
        top:           auto !important;
        bottom:        0 !important;
        left:          0 !important;
        transform:     translateY(100%) !important;
        max-height:    90vh;
    }}
    #cart-modal.open {{ transform: translateY(0) !important; }}
}}
"""
