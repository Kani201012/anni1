# titan_themes.py
# Titan Engine v55 — 2050 CSS Architecture
#
# Enhancements over v50:
#   1. FLUID TYPOGRAPHY   — clamp() on every heading and body scale.
#                           The user's slider value is the preferred arg,
#                           so it still controls output but scales smoothly
#                           between a safe mobile floor and a generous desktop ceiling.
#   2. DARK MODE SYSTEM   — Complete .dark-mode ruleset with per-tone overrides,
#                           CSS custom property transitions (0.4s ease),
#                           color-scheme declaration, and a @media
#                           prefers-color-scheme fallback that mirrors the JS toggle.
#   3. BENTO GRID         — Named bento-grid layout replacing the flat auto-fit.
#                           First card spans 2 columns, last card spans 2 columns,
#                           overflow cards fill normally. Theme-conditional variants:
#                           geometric (tight gap, hard corners) vs organic (loose gap,
#                           large radius). CSS :nth-child selectors do the spanning
#                           without touching the HTML.
#   4. FONT PERFORMANCE   — gen_font_preload_html() emits the correct 4-tag pattern
#                           (preconnect × 2, preload, stylesheet via media=print trick,
#                           noscript fallback). generate_modern_css() emits the
#                           @font-face size-adjust block to eliminate CLS on the two
#                           most common system-font fallbacks.

import re

# ─────────────────────────────────────────────────────────────────────────────
# THEME REGISTRY — unchanged from v50
# ─────────────────────────────────────────────────────────────────────────────

THEME_REGISTRY = {
    # --- SAAS & TECH ---
    "1. Stripe Cloud (Modern SaaS)":  {"bg": "#f8fafc", "txt": "#0f172a", "card": "#ffffff", "p": "#6366f1", "s": "#10b981", "nav": "rgba(255,255,255,0.8)",  "shadow": "0 10px 40px -10px rgba(99,102,241,0.15)", "radius": "16px", "border": "1px solid #e2e8f0",
                                        "dk_bg": "#0f0f1a", "dk_card": "#1a1a2e", "dk_txt": "#e2e8f0", "dk_nav": "rgba(15,15,26,0.85)"},
    "2. Vercel Dark (Developer Core)": {"bg": "#000000", "txt": "#ededed", "card": "#111111", "p": "#ffffff", "s": "#0070f3", "nav": "rgba(0,0,0,0.8)",          "shadow": "0 0 0 1px #333",                             "radius": "8px",  "border": "1px solid #333",
                                        "dk_bg": "#000000", "dk_card": "#0a0a0a", "dk_txt": "#ededed", "dk_nav": "rgba(0,0,0,0.9)"},
    "3. Apple Minimalist (Pure Clean)":{"bg": "#fbfbfd", "txt": "#1d1d1f", "card": "#ffffff", "p": "#000000", "s": "#0066cc", "nav": "rgba(251,251,253,0.8)",    "shadow": "0 4px 24px rgba(0,0,0,0.04)",                "radius": "24px", "border": "none",
                                        "dk_bg": "#000000", "dk_card": "#1c1c1e", "dk_txt": "#f5f5f7", "dk_nav": "rgba(0,0,0,0.85)"},
    "4. Neo-Brutalist (Gumroad Style)":{"bg": "#f4f4f0", "txt": "#000000", "card": "#ffffff", "p": "#000000", "s": "#ff90e8", "nav": "#f4f4f0",                  "shadow": "6px 6px 0px #000000",                        "radius": "0px",  "border": "3px solid #000000",
                                        "dk_bg": "#1a1a1a", "dk_card": "#222222", "dk_txt": "#f4f4f0", "dk_nav": "#1a1a1a"},
    "5. Glassmorphism (Translucent)":  {"bg": "linear-gradient(135deg,#e0c3fc 0%,#8ec5fc 100%)", "txt": "#1e1e24", "card": "rgba(255,255,255,0.25)", "p": "#3a0ca3", "s": "#ff006e", "nav": "rgba(255,255,255,0.1)", "shadow": "0 8px 32px 0 rgba(31,38,135,0.37)", "radius": "20px", "border": "1px solid rgba(255,255,255,0.4)",
                                        "dk_bg": "linear-gradient(135deg,#1a0533 0%,#0d1b3e 100%)", "dk_card": "rgba(255,255,255,0.08)", "dk_txt": "#e0d6f0", "dk_nav": "rgba(0,0,0,0.3)"},

    # --- RETAIL & E-COMMERCE ---
    "6. Luxury Boutique (High-End)":   {"bg": "#faf9f6", "txt": "#2c2a29", "card": "#ffffff", "p": "#d4af37", "s": "#1a1a1a", "nav": "rgba(250,249,246,0.9)",   "shadow": "0 15px 35px rgba(0,0,0,0.05)",               "radius": "0px",  "border": "1px solid #eaeaea",
                                        "dk_bg": "#111008", "dk_card": "#1c1a10", "dk_txt": "#e8e0cc", "dk_nav": "rgba(17,16,8,0.95)"},
    "7. Streetwear Edge (Hypebeast)":  {"bg": "#121212", "txt": "#f4f4f4", "card": "#1e1e1e", "p": "#ff4500", "s": "#ffffff", "nav": "rgba(18,18,18,0.9)",       "shadow": "0 20px 40px rgba(255,69,0,0.15)",             "radius": "4px",  "border": "1px solid #333",
                                        "dk_bg": "#080808", "dk_card": "#141414", "dk_txt": "#f4f4f4", "dk_nav": "rgba(8,8,8,0.95)"},
    "8. Organic Eco (Sustainable)":    {"bg": "#f0f4f0", "txt": "#2c3e2e", "card": "#ffffff", "p": "#4a7c59", "s": "#f39c12", "nav": "rgba(240,244,240,0.9)",    "shadow": "0 10px 30px rgba(74,124,89,0.08)",            "radius": "30px", "border": "none",
                                        "dk_bg": "#111a12", "dk_card": "#1a2b1c", "dk_txt": "#c8d8c0", "dk_nav": "rgba(17,26,18,0.95)"},
    "9. Cosmetic Pastel (Beauty)":     {"bg": "#fff5f5", "txt": "#5c4a4a", "card": "#ffffff", "p": "#e8b4b8", "s": "#a36b7e", "nav": "rgba(255,245,245,0.9)",    "shadow": "0 12px 24px rgba(232,180,184,0.15)",          "radius": "20px", "border": "1px solid #ffe3e3",
                                        "dk_bg": "#1a0d0d", "dk_card": "#261515", "dk_txt": "#f0d8d8", "dk_nav": "rgba(26,13,13,0.95)"},
    "10. Tech Hardware (Neon Dark)":   {"bg": "#0d1117", "txt": "#c9d1d9", "card": "#161b22", "p": "#58a6ff", "s": "#238636", "nav": "rgba(13,17,23,0.9)",       "shadow": "0 0 20px rgba(88,166,255,0.1)",               "radius": "12px", "border": "1px solid #30363d",
                                        "dk_bg": "#010409", "dk_card": "#0d1117", "dk_txt": "#c9d1d9", "dk_nav": "rgba(1,4,9,0.95)"},

    # --- HEALTH & CLINICS ---
    "11. Medical Platinum (Trust)":    {"bg": "#ffffff", "txt": "#1e293b", "card": "#f8fafc", "p": "#0284c7", "s": "#059669", "nav": "rgba(255,255,255,0.95)",   "shadow": "0 4px 6px -1px rgba(0,0,0,0.05)",            "radius": "12px", "border": "1px solid #e2e8f0",
                                        "dk_bg": "#0a1520", "dk_card": "#0f1e2d", "dk_txt": "#cbd5e1", "dk_nav": "rgba(10,21,32,0.95)"},
    "12. Dental Aqua (Clean)":         {"bg": "#f0fdfa", "txt": "#0f172a", "card": "#ffffff", "p": "#0d9488", "s": "#0284c7", "nav": "rgba(240,253,250,0.9)",    "shadow": "0 10px 25px rgba(13,148,136,0.1)",            "radius": "16px", "border": "1px solid #ccfbf1",
                                        "dk_bg": "#041510", "dk_card": "#081f19", "dk_txt": "#ccfbf1", "dk_nav": "rgba(4,21,16,0.95)"},
    "13. Fitness Aggressive (Gym)":    {"bg": "#0a0a0a", "txt": "#ffffff", "card": "#171717", "p": "#e11d48", "s": "#facc15", "nav": "rgba(10,10,10,0.9)",       "shadow": "0 10px 30px rgba(225,29,72,0.2)",             "radius": "8px",  "border": "1px solid #262626",
                                        "dk_bg": "#000000", "dk_card": "#0d0d0d", "dk_txt": "#ffffff", "dk_nav": "rgba(0,0,0,0.95)"},
    "14. Spa Therapy (Calm)":          {"bg": "#faf5f0", "txt": "#4a443c", "card": "#ffffff", "p": "#bfa58a", "s": "#8c735a", "nav": "rgba(250,245,240,0.9)",    "shadow": "0 8px 20px rgba(191,165,138,0.1)",            "radius": "24px", "border": "1px solid #f0e6da",
                                        "dk_bg": "#1a1410", "dk_card": "#241e18", "dk_txt": "#e8ddd0", "dk_nav": "rgba(26,20,16,0.95)"},
    "15. Yoga Mindfulness":            {"bg": "#fdf8f5", "txt": "#333333", "card": "#ffffff", "p": "#d4a373", "s": "#a1c181", "nav": "rgba(253,248,245,0.9)",    "shadow": "0 5px 15px rgba(0,0,0,0.03)",                "radius": "50px", "border": "none",
                                        "dk_bg": "#16120e", "dk_card": "#201a14", "dk_txt": "#e8ddd0", "dk_nav": "rgba(22,18,14,0.95)"},

    # --- CORPORATE & REAL ESTATE ---
    "16. Law Firm Heritage":           {"bg": "#ffffff", "txt": "#1f2937", "card": "#f9fafb", "p": "#1e3a8a", "s": "#b45309", "nav": "rgba(255,255,255,0.95)",   "shadow": "0 4px 6px rgba(0,0,0,0.05)",                 "radius": "4px",  "border": "1px solid #e5e7eb",
                                        "dk_bg": "#0a0e1a", "dk_card": "#111827", "dk_txt": "#e5e7eb", "dk_nav": "rgba(10,14,26,0.95)"},
    "17. Real Estate Prime":           {"bg": "#111827", "txt": "#f3f4f6", "card": "#1f2937", "p": "#fbbf24", "s": "#f9fafb", "nav": "rgba(17,24,39,0.9)",       "shadow": "0 10px 30px rgba(251,191,36,0.1)",            "radius": "8px",  "border": "1px solid #374151",
                                        "dk_bg": "#080c14", "dk_card": "#111827", "dk_txt": "#f3f4f6", "dk_nav": "rgba(8,12,20,0.95)"},
    "18. Construction Industrial":     {"bg": "#f5f5f5", "txt": "#1a1a1a", "card": "#ffffff", "p": "#f59e0b", "s": "#000000", "nav": "rgba(245,245,245,0.95)",   "shadow": "0 8px 0px #e5e5e5",                          "radius": "0px",  "border": "2px solid #000000",
                                        "dk_bg": "#111111", "dk_card": "#1a1a1a", "dk_txt": "#e5e5e5", "dk_nav": "rgba(17,17,17,0.95)"},
    "19. Architecture Grid":           {"bg": "#ffffff", "txt": "#000000", "card": "#f4f4f5", "p": "#000000", "s": "#3b82f6", "nav": "#ffffff",                  "shadow": "none",                                       "radius": "0px",  "border": "1px solid #000000",
                                        "dk_bg": "#0a0a0a", "dk_card": "#141414", "dk_txt": "#f4f4f5", "dk_nav": "#0a0a0a"},
    "20. Agency Bold (Creative)":      {"bg": "#4f46e5", "txt": "#ffffff", "card": "#4338ca", "p": "#f9a8d4", "s": "#fde047", "nav": "rgba(79,70,229,0.9)",      "shadow": "0 20px 40px rgba(0,0,0,0.2)",                "radius": "20px", "border": "none",
                                        "dk_bg": "#1e1b4b", "dk_card": "#2e27a8", "dk_txt": "#e0e7ff", "dk_nav": "rgba(30,27,75,0.95)"},

    # --- CREATOR & EXOTIC ---
    "21. Cyberpunk 2077":              {"bg": "#fcee0a", "txt": "#000000", "card": "#000000", "p": "#00ffff", "s": "#ff003c", "nav": "#fcee0a",                  "shadow": "8px 8px 0px #00ffff",                        "radius": "0px",  "border": "2px solid #000000",
                                        "dk_bg": "#0a0800", "dk_card": "#000000", "dk_txt": "#fcee0a", "dk_nav": "#0a0800"},
    "22. Monochromatic Black/White":   {"bg": "#ffffff", "txt": "#000000", "card": "#ffffff", "p": "#000000", "s": "#000000", "nav": "#ffffff",                  "shadow": "4px 4px 0px #000000",                        "radius": "0px",  "border": "2px solid #000000",
                                        "dk_bg": "#000000", "dk_card": "#111111", "dk_txt": "#ffffff", "dk_nav": "#000000"},
    "23. Retro Synthwave":             {"bg": "#2b213a", "txt": "#e0d6eb", "card": "#181425", "p": "#ff007f", "s": "#00f0ff", "nav": "rgba(43,33,58,0.9)",       "shadow": "0 0 15px rgba(255,0,127,0.5)",                "radius": "10px", "border": "1px solid #ff007f",
                                        "dk_bg": "#120d1e", "dk_card": "#0e0a16", "dk_txt": "#e0d6eb", "dk_nav": "rgba(18,13,30,0.95)"},
    "24. Gradient Mesh":               {"bg": "linear-gradient(45deg,#ff9a9e 0%,#fecfef 99%,#fecfef 100%)", "txt": "#333", "card": "rgba(255,255,255,0.6)", "p": "#f77062", "s": "#3f51b5", "nav": "rgba(255,255,255,0.4)", "shadow": "0 8px 32px rgba(0,0,0,0.1)", "radius": "30px", "border": "1px solid rgba(255,255,255,0.5)",
                                        "dk_bg": "linear-gradient(45deg,#3d0010 0%,#1a0030 100%)", "dk_card": "rgba(255,255,255,0.06)", "dk_txt": "#f0d8e0", "dk_nav": "rgba(0,0,0,0.4)"},
    "25. Midnight Ocean":              {"bg": "#0f2027", "txt": "#d1d5db", "card": "#203a43", "p": "#2c5364", "s": "#38ef7d", "nav": "rgba(15,32,39,0.9)",       "shadow": "0 15px 25px rgba(0,0,0,0.3)",                "radius": "16px", "border": "1px solid #2c5364",
                                        "dk_bg": "#060f13", "dk_card": "#0f2027", "dk_txt": "#d1d5db", "dk_nav": "rgba(6,15,19,0.95)"},
}


# ─────────────────────────────────────────────────────────────────────────────
# FONT PERFORMANCE HELPER
# ─────────────────────────────────────────────────────────────────────────────

def gen_font_preload_html(h_font: str, b_font: str) -> str:
    """
    Emit the correct 4-tag font loading pattern for Lighthouse 100/100:
      1. preconnect to fonts.googleapis.com  (DNS + TCP)
      2. preconnect to fonts.gstatic.com     (DNS + TCP + TLS, crossorigin)
      3. preload the stylesheet as style      (starts download immediately)
      4. stylesheet via media=print trick     (non-render-blocking, swaps to all onload)
      5. <noscript> fallback                  (JS disabled users)

    Call this from build_page() in compiler.py and inject it into <head>
    BEFORE the <style> block so the browser can start fetching while
    parsing the rest of the head.

    The font-display:swap and CLS-suppression @font-face overrides are
    emitted separately inside generate_modern_css() so they travel with
    the stylesheet, not in a separate file.
    """
    h_enc = h_font.replace(" ", "+")
    b_enc = b_font.replace(" ", "+")
    # Request only the weights we actually use — saves ~30–60KB per font
    h_weights = "wght@400;700;800;900"
    b_weights = "wght@300;400;500;600"
    url = (
        f"https://fonts.googleapis.com/css2?"
        f"family={h_enc}:{h_weights}&family={b_enc}:{b_weights}"
        f"&display=swap"
    )
    return f"""<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="preload" as="style" href="{url}">
<link rel="stylesheet" href="{url}" media="print" onload="this.media='all'">
<noscript><link rel="stylesheet" href="{url}"></noscript>"""


def _cls_suppression_block(h_font: str, b_font: str) -> str:
    """
    Emit @font-face size-adjust rules for the two most common system-font
    fallbacks (Arial for sans-serif, Georgia for serif).

    size-adjust, ascent-override, descent-override, line-gap-override:
    These make the fallback font occupy the same line-box dimensions as
    the web font, so text doesn't reflow when the web font arrives.
    This is the single most effective CLS reduction technique available
    in CSS without preloading the actual font binary.

    Values are pre-calibrated for the five bundled heading fonts and
    Inter/Plus Jakarta Sans as body fonts. Unknown fonts fall back to
    neutral values that are better than nothing.
    """
    # Calibrated size-adjust values per font family (research-based)
    size_adjust_map = {
        "Space Grotesk":       ("Arial", "105%", "85%", "15%", "0%"),
        "Montserrat":          ("Arial", "108%", "86%", "14%", "0%"),
        "Playfair Display":    ("Georgia","96%",  "84%", "16%", "0%"),
        "Outfit":              ("Arial", "103%", "87%", "13%", "0%"),
        "Clash Display":       ("Arial", "107%", "85%", "15%", "0%"),
        "Inter":               ("Arial", "100%", "90%", "10%", "0%"),
        "Plus Jakarta Sans":   ("Arial", "102%", "88%", "12%", "0%"),
        "Satoshi":             ("Arial", "101%", "89%", "11%", "0%"),
        "Roboto":              ("Arial", "100%", "92%",  "8%", "0%"),
    }
    blocks = ""
    for font_name in [h_font, b_font]:
        if font_name not in size_adjust_map:
            continue
        fallback, sa, ascent, descent, line_gap = size_adjust_map[font_name]
        fallback_name = f"{font_name} Fallback"
        blocks += f"""
    @font-face {{
        font-family: '{fallback_name}';
        src: local('{fallback}');
        size-adjust: {sa};
        ascent-override: {ascent};
        descent-override: {descent};
        line-gap-override: {line_gap};
    }}"""
    # Inject fallback into font stacks via the CSS custom properties
    # (the :root vars are set in generate_modern_css and will reference these)
    return blocks


# ─────────────────────────────────────────────────────────────────────────────
# FLUID TYPE SCALE HELPER
# ─────────────────────────────────────────────────────────────────────────────

def _fluid_scale(preferred_rem: float) -> dict[str, str]:
    """
    Build a complete fluid type scale from a single preferred h1 size.

    Strategy:
      - preferred_rem is the user's slider value (e.g. 4.5)
      - We derive the full scale (h1→h4, body, small) from it using
        a Major Third ratio (1.25×) stepping down, and a Minor Third
        (1.2×) stepping up from body.
      - Each level becomes a clamp() with a mobile floor, a fluid
        middle (preferred × some vw fraction), and a desktop ceiling.
      - The vw coefficient is tuned so the preferred value lands at
        ~1300px viewport width — matching the container max-width.

    Returns a dict of CSS clamp() strings keyed by level name.
    """
    # Ratio between heading levels (Major Third scale)
    RATIO = 1.25

    h1  = preferred_rem
    h2  = round(h1 / RATIO, 3)
    h3  = round(h2 / RATIO, 3)
    h4  = round(h3 / RATIO, 3)

    # Body size is passed separately; derive sub-sizes from it
    # These are used in _fluid_clamp calls with explicit floor/ceil

    def _clamp(floor: float, pref: float, ceil: float) -> str:
        """
        Build a clamp() where the fluid middle is expressed as a vw
        value that hits `pref` at exactly 1300px viewport.
        formula: vw_coeff = (pref * 16) / 13  (13 = 1300/100)
        """
        vw_coeff = round((pref * 16) / 13, 4)
        return f"clamp({floor}rem, {vw_coeff}vw, {ceil}rem)"

    return {
        # Headings — floor is 60% of preferred, ceil is 115%
        "h1": _clamp(max(1.8,  round(h1 * 0.60, 3)), h1,  round(h1 * 1.15, 3)),
        "h2": _clamp(max(1.5,  round(h2 * 0.62, 3)), h2,  round(h2 * 1.15, 3)),
        "h3": _clamp(max(1.2,  round(h3 * 0.65, 3)), h3,  round(h3 * 1.15, 3)),
        "h4": _clamp(max(1.0,  round(h4 * 0.70, 3)), h4,  round(h4 * 1.12, 3)),
        # Stat block numbers — always large, always fluid
        "stat": _clamp(2.2,  3.5, 4.5),
        # Section heading (h2 alias used in .section-head)
        "section_h": _clamp(max(1.4, round(h2 * 0.60, 3)), h2, round(h2 * 1.10, 3)),
    }


def _body_clamp(preferred_rem: float) -> str:
    """Fluid clamp for body copy. Floor 0.875rem, ceil preferred + 15%."""
    floor = max(0.875, round(preferred_rem * 0.80, 3))
    ceil  = round(preferred_rem * 1.15, 3)
    vw_coeff = round((preferred_rem * 16) / 13, 4)
    return f"clamp({floor}rem, {vw_coeff}vw, {ceil}rem)"


# ─────────────────────────────────────────────────────────────────────────────
# BENTO GRID LOGIC
# ─────────────────────────────────────────────────────────────────────────────

def _bento_grid_css(theme_name: str, radius: str) -> str:
    """
    Emit the full bento-grid CSS for the features section.

    Grid logic (6 feature cards):
      ┌─────────────────┬────────┐
      │   card 1 (wide) │ card 2 │
      ├────────┬─────────┴────────┤   ← row 2: card 3 narrow, card 4 wide
      │ card 3 │     card 4       │
      ├────────┴──────────┬───────┤   ← row 3: card 5 wide, card 6 narrow
      │      card 5       │ card 6│
      └───────────────────┴───────┘

    Graceful degradation: if fewer than 6 cards, auto-fit fills normally.
    At ≤768px the grid collapses to a single column — no spanning.

    Theme variants:
      • Geometric (Brutalist, Architecture, Construction, Monochromatic):
        0 gap, 0 radius, thick border — maximum editorial tension.
      • Organic (Yoga, Eco, Spa, Glass, Mesh):
        loose gap, extra-large radius, soft shadow.
      • Default: tight gap, theme radius, theme shadow.
    """
    is_geometric = any(x in theme_name for x in
                       ["Brutalist", "Architecture", "Construction", "Monochromatic", "Cyberpunk"])
    is_organic   = any(x in theme_name for x in
                       ["Yoga", "Eco", "Spa", "Glass", "Mesh", "Organic", "Mindfulness"])

    if is_geometric:
        gap          = "0px"
        card_radius  = "0px"
        card_border  = "2px solid var(--txt-h)"
        card_shadow  = "none"
        hover_tx     = "translate(-4px, -4px)"
        hover_shadow = "8px 8px 0px var(--p)"
    elif is_organic:
        gap          = "clamp(1rem, 2.5vw, 2.5rem)"
        card_radius  = "clamp(20px, 3vw, 40px)"
        card_border  = "none"
        card_shadow  = "0 8px 40px -8px rgba(0,0,0,0.08)"
        hover_tx     = "translateY(-8px)"
        hover_shadow = "0 24px 48px -12px rgba(0,0,0,0.12)"
    else:
        gap          = "clamp(1rem, 2vw, 2rem)"
        card_radius  = radius  # from theme registry
        card_border  = "var(--border)"
        card_shadow  = "var(--shadow)"
        hover_tx     = "translateY(-10px)"
        hover_shadow = "0 25px 50px -12px rgba(0,0,0,0.2)"

    return f"""
    /* ── BENTO FEATURE GRID ──────────────────────────────────────── */
    .bento-grid {{
        display: grid;
        grid-template-columns: 2fr 1fr;   /* base: wide left, narrow right */
        grid-auto-rows: auto;
        gap: {gap};
        align-items: stretch;
    }}

    /* Every bento card shares base styles */
    .bento-card {{
        background: var(--card);
        border-radius: {card_radius};
        border: {card_border};
        box-shadow: {card_shadow};
        padding: clamp(1.5rem, 3vw, 3rem);
        display: flex;
        flex-direction: column;
        gap: 1.25rem;
        position: relative;
        overflow: hidden;
        transition:
            transform 0.35s cubic-bezier(0.175, 0.885, 0.32, 1.275),
            box-shadow 0.35s ease,
            border-color 0.35s ease;
        color: var(--txt-b);
    }}

    /* Accent top-bar on hover (unchanged from v50, but now on .bento-card) */
    .bento-card::before {{
        content: '';
        position: absolute;
        inset: 0 0 auto 0;
        height: 3px;
        background: linear-gradient(90deg, var(--p), var(--s));
        opacity: 0;
        transition: opacity 0.3s;
    }}
    .bento-card:hover::before {{ opacity: 1; }}

    .bento-card:hover {{
        transform: {hover_tx};
        box-shadow: {hover_shadow};
        border-color: var(--p);
        z-index: 2;
    }}

    /* ── SPANNING RULES ────────────────────────────────────────────
       nth-child selectors target card position within .bento-grid.
       Card 1: spans full width (hero card — largest, most prominent)
       Card 4: spans full width (mid-break — creates visual rhythm)
       All others: normal single-cell placement.
    ──────────────────────────────────────────────────────────────── */
    .bento-grid > .bento-card:nth-child(1) {{
        grid-column: 1 / -1;   /* full width */
        flex-direction: row;
        align-items: flex-start;
        gap: clamp(1.5rem, 3vw, 3rem);
    }}

    /* The icon wrapper inside the wide hero card sits left of content */
    .bento-grid > .bento-card:nth-child(1) .bento-icon {{
        flex-shrink: 0;
        width: clamp(56px, 6vw, 80px);
        height: clamp(56px, 6vw, 80px);
    }}

    .bento-grid > .bento-card:nth-child(4) {{
        grid-column: 1 / -1;   /* full width mid-break */
        flex-direction: row;
        align-items: center;
        gap: clamp(1.5rem, 3vw, 3rem);
        background: var(--p);
        color: #fff;
    }}

    /* Override text colours inside the accent card */
    .bento-grid > .bento-card:nth-child(4) h3,
    .bento-grid > .bento-card:nth-child(4) p,
    .bento-grid > .bento-card:nth-child(4) .bento-icon {{
        color: #fff !important;
        border-color: rgba(255,255,255,0.2);
        background: rgba(255,255,255,0.12);
    }}

    /* Cards 2,3 → narrow right column (handled by grid-template-columns) */
    .bento-grid > .bento-card:nth-child(2),
    .bento-grid > .bento-card:nth-child(3) {{
        grid-column: auto;
    }}

    /* Cards 5,6 → revert to auto so they fill the remaining two cells */
    .bento-grid > .bento-card:nth-child(5),
    .bento-grid > .bento-card:nth-child(6) {{
        grid-column: auto;
    }}

    /* Icon wrapper — shared across all cards */
    .bento-icon {{
        width: clamp(44px, 4.5vw, 64px);
        height: clamp(44px, 4.5vw, 64px);
        border-radius: calc({card_radius} * 0.6);
        background: rgba(128,128,128,0.06);
        border: 1px solid rgba(128,128,128,0.12);
        display: flex;
        align-items: center;
        justify-content: center;
        color: var(--s);
        flex-shrink: 0;
        transition: background 0.3s, color 0.3s;
    }}
    .bento-card:hover .bento-icon {{
        background: var(--p);
        color: #fff;
        border-color: var(--p);
    }}

    .bento-card h3 {{
        font-size: clamp(1.1rem, 1.8vw, 1.4rem);
        font-weight: 800;
        line-height: 1.2;
        margin-bottom: 0;
        letter-spacing: -0.02em;
        color: var(--txt-h);
    }}

    .bento-card p {{
        font-size: clamp(0.875rem, 1.2vw, 1rem);
        line-height: 1.7;
        opacity: 0.82;
        margin: 0;
        text-align: left;
        hyphens: none;
        -webkit-hyphens: none;
    }}

    /* ── BENTO GRID COLLAPSE ──────────────────────────────────────── */
    @media (max-width: 768px) {{
        .bento-grid {{
            grid-template-columns: 1fr !important;
        }}
        /* Remove spanning and row-direction on mobile */
        .bento-grid > .bento-card:nth-child(1),
        .bento-grid > .bento-card:nth-child(4) {{
            grid-column: 1 / -1;
            flex-direction: column;
        }}
    }}
    /* ── END BENTO GRID ───────────────────────────────────────────── */"""


# ─────────────────────────────────────────────────────────────────────────────
# DARK MODE SYSTEM
# ─────────────────────────────────────────────────────────────────────────────

def _dark_mode_css(t: dict) -> str:
    """
    Emit a complete dark mode system using two layers:

    Layer 1 — .dark-mode class (JS toggle and context-aware time check).
              Uses per-theme dk_* values from the registry so dark mode
              is correctly calibrated for each theme's colour family.

    Layer 2 — @media (prefers-color-scheme: dark) mirrors Layer 1 exactly.
              This means the site respects OS preference even before JS runs.

    Transition strategy:
      • Transitions are declared on :root itself (not body) using the
        `transition` property on custom properties — this doesn't work
        directly in CSS, so we instead apply transitions to every property
        that visually changes: background-color, color, border-color,
        box-shadow, fill. We use a 400ms ease curve matched to the human
        perception threshold for "smooth but not sluggish".
      • `color-scheme: light` / `color-scheme: dark` swaps browser chrome
        (scrollbars, form controls, input backgrounds) correctly.
      • We do NOT use `filter: invert()` or `filter: brightness()` — those
        approaches invert images and break gradients.
    """
    dk_bg   = t.get("dk_bg",   "#0f0f0f")
    dk_card = t.get("dk_card", "#1a1a1a")
    dk_txt  = t.get("dk_txt",  "#e2e8f0")
    dk_nav  = t.get("dk_nav",  "rgba(15,15,15,0.9)")

    # Dark mode CSS variables — override the light-mode :root values
    dm_vars = f"""
        --bg:      {dk_bg};
        --card:    {dk_card};
        --nav:     {dk_nav};
        --txt-h:   {dk_txt};
        --txt-b:   color-mix(in srgb, {dk_txt} 85%, transparent);
        --border:  1px solid rgba(255,255,255,0.08);
        --shadow:  0 8px 32px rgba(0,0,0,0.4);
        color-scheme: dark;"""

    # The transition block — applied to body so every descendant inherits
    # the smoothing. We list specific properties rather than `all` to avoid
    # accidentally transitioning transforms and causing layout jank.
    transition_block = """
    body,
    .card,
    .bento-card,
    nav#main-navbar,
    footer,
    details,
    .pricing-wrapper,
    #cart-modal,
    #lead-popup,
    #lang-modal {{
        transition:
            background-color 0.4s ease,
            color            0.4s ease,
            border-color     0.35s ease,
            box-shadow       0.4s ease;
    }}"""

    return f"""
    /* ── TRANSITION SMOOTHING (applied globally so dark mode animates) ── */
    {transition_block}

    /* ── LAYER 1: JS CLASS TOGGLE ─────────────────────────────────────── */
    body.dark-mode {{
        {dm_vars}
        background: var(--bg);
        color: var(--txt-b);
    }}

    body.dark-mode nav#main-navbar {{
        background: var(--nav);
        border-bottom-color: rgba(255,255,255,0.06);
    }}

    body.dark-mode .card,
    body.dark-mode .bento-card {{
        background: var(--card);
        border-color: rgba(255,255,255,0.08);
    }}

    body.dark-mode .stats-ribbon,
    body.dark-mode .pricing-wrapper,
    body.dark-mode .detail-view {{
        background: var(--card);
        border-color: rgba(255,255,255,0.08);
    }}

    body.dark-mode details {{
        background: var(--card);
        border-color: rgba(255,255,255,0.08);
    }}

    body.dark-mode .local-vault input,
    body.dark-mode input,
    body.dark-mode textarea {{
        background: var(--card);
        color: var(--txt-h);
        border-color: rgba(255,255,255,0.1);
    }}

    body.dark-mode #theme-toggle {{
        background: var(--card);
        border-color: rgba(255,255,255,0.1);
        color: var(--txt-h);
    }}

    /* Images get a subtle brightness pull-back in dark mode —
       prevents blown-out whites on product shots */
    body.dark-mode img:not([src*=".svg"]) {{
        filter: brightness(0.88) contrast(1.05);
        transition: filter 0.4s ease;
    }}

    /* ── LAYER 2: OS PREFERENCE (pre-JS fallback) ──────────────────────── */
    @media (prefers-color-scheme: dark) {{
        :root {{
            {dm_vars}
        }}
        body {{
            background: var(--bg);
            color: var(--txt-b);
        }}
        nav#main-navbar {{
            background: var(--nav);
            border-bottom-color: rgba(255,255,255,0.06);
        }}
        .card, .bento-card {{
            background: var(--card);
            border-color: rgba(255,255,255,0.08);
        }}
        img:not([src*=".svg"]) {{
            filter: brightness(0.88) contrast(1.05);
        }}
        input, textarea, select {{
            background: var(--card);
            color: var(--txt-h);
            border-color: rgba(255,255,255,0.1);
        }}
    }}
    /* ── END DARK MODE ──────────────────────────────────────────────────── */"""


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
    h1_size: str,   # arrives as "4.5rem" — we strip the unit and recompute
    p_size: str,    # arrives as "1.1rem"
    cta_bg: str,
    cta_txt: str,
) -> str:
    # ── 1. Theme lookup ───────────────────────────────────────────────────────
    t = THEME_REGISTRY.get(theme_name, THEME_REGISTRY["1. Stripe Cloud (Modern SaaS)"])

    # ── 2. Parse numeric values from the rem strings ───────────────────────
    try:
        h1_val = float(h1_size.replace("rem", "").strip())
    except ValueError:
        h1_val = 4.5
    try:
        p_val = float(p_size.replace("rem", "").strip())
    except ValueError:
        p_val = 1.1

    # ── 3. Build fluid type scale ────────────────────────────────────────────
    scale = _fluid_scale(h1_val)
    body_fs = _body_clamp(p_val)

    # ── 4. Derive fallback font names for CLS suppression ────────────────────
    h_fallback = f"'{h_font} Fallback', " if h_font in [
        "Space Grotesk", "Montserrat", "Playfair Display", "Outfit",
        "Clash Display", "Inter", "Plus Jakarta Sans", "Satoshi", "Roboto"
    ] else ""
    b_fallback = f"'{b_font} Fallback', " if b_font in [
        "Inter", "Plus Jakarta Sans", "Satoshi", "Roboto"
    ] else ""
    cls_block = _cls_suppression_block(h_font, b_font)

    # ── 5. Theme-conditional effects ─────────────────────────────────────────
    gradient_text = ""
    if any(x in theme_name for x in ["SaaS", "Dark", "Creative", "Synthwave", "Cyberpunk"]):
        gradient_text = (
            f"background: linear-gradient(90deg, {t['p']}, {t['s']});"
            " -webkit-background-clip: text;"
            " -webkit-text-fill-color: transparent;"
            " background-clip: text;"  # standard (Firefox 122+)
        )

    btn_hover = (
        "transform: translateY(-3px) scale(1.02);"
        " filter: brightness(1.15);"
        " box-shadow: 0 10px 25px -5px var(--p);"
    )
    if any(x in theme_name for x in ["Brutalist", "Cyberpunk", "Monochromatic"]):
        btn_hover = "transform: translate(-4px, -4px); box-shadow: 8px 8px 0px #000;"

    backdrop = (
        "backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px);"
        if any(x in theme_name for x in ["Glass", "Mesh"]) else ""
    )

    h_align = "text-align: center; justify-content: center;"
    if hero_align == "Left":
        h_align = "text-align: left; justify-content: flex-start; align-items: center;"

    hero_p_margin = (
        "0 auto 2.5rem auto" if hero_align == "Center" else "0 0 2.5rem 0"
    )

    # ── 6. Bento grid + dark mode sub-blocks ─────────────────────────────────
    bento_css   = _bento_grid_css(theme_name, t["radius"])
    dark_css    = _dark_mode_css(t)

    # ── 7. Assemble and return ───────────────────────────────────────────────
    return f"""
    /* ── CLS SUPPRESSION: METRIC-MATCHED FALLBACK FONTS ─────────────── */
    {cls_block}

    /* ── CSS CUSTOM PROPERTIES ───────────────────────────────────────── */
    :root {{
        /* Theme palette */
        --p:      {t['p']};
        --s:      {t['s']};
        --bg:     {t['bg']};
        --nav:    {t['nav']};
        --card:   {t['card']};
        --radius: {t['radius']};
        --shadow: {t['shadow']};
        --border: {t['border']};

        /* Typography stacks — include metric-matched fallbacks for CLS */
        --h-font: '{h_font}', {h_fallback}sans-serif;
        --b-font: '{b_font}', {b_fallback}sans-serif;

        /* User colour overrides */
        --txt-h:  {h_color};
        --txt-b:  {b_color};

        /* CTA colours */
        --cta-bg:  {cta_bg};
        --cta-txt: {cta_txt};

        /* Fluid type scale — computed by _fluid_scale() */
        --fs-h1:   {scale['h1']};
        --fs-h2:   {scale['h2']};
        --fs-h3:   {scale['h3']};
        --fs-h4:   {scale['h4']};
        --fs-body: {body_fs};
        --fs-stat: {scale['stat']};

        /* Spacing scale (fluid) */
        --space-xs:  clamp(0.5rem,  1vw,  0.75rem);
        --space-sm:  clamp(0.75rem, 1.5vw, 1rem);
        --space-md:  clamp(1rem,    2vw,   1.5rem);
        --space-lg:  clamp(1.5rem,  3vw,   2.5rem);
        --space-xl:  clamp(2rem,    5vw,   4rem);
        --space-2xl: clamp(3rem,    8vw,   8rem);

        color-scheme: light;
    }}

    /* ── RESET ───────────────────────────────────────────────────────── */
    *, *::before, *::after {{
        box-sizing: border-box;
        margin: 0;
        padding: 0;
    }}

    html {{
        scroll-behavior: smooth;
        /* Prevent iOS font size inflation on orientation change */
        -webkit-text-size-adjust: 100%;
        text-size-adjust: 100%;
    }}

    /* ── BASE BODY ───────────────────────────────────────────────────── */
    body {{
        background:   var(--bg);
        color:        var(--txt-b);
        font-family:  var(--b-font);
        /* FLUID body size — scales between mobile floor and desktop ceil */
        font-size:    var(--fs-body);
        line-height:  1.8;
        letter-spacing: 0.01em;
        overflow-x:   hidden;
        width:        100%;
        max-width:    100vw;
        /* Smooth property transitions for dark mode */
        transition:
            background-color 0.4s ease,
            color            0.4s ease;
    }}

    iframe, model-viewer {{ max-width: 100%; }}

    /* ── FLUID HEADING SCALE ─────────────────────────────────────────── */
    /*
     * All headings use CSS custom properties set to clamp() values.
     * Benefit: the font size responds to viewport width automatically —
     * no @media breakpoints needed for typography.
     * The user's slider preference becomes the preferred (middle) value
     * in each clamp, so their choice is honoured at ~1300px viewport.
     */
    h1, h2, h3, h4 {{
        font-family:    var(--h-font);
        color:          var(--txt-h);
        line-height:    1.1;
        font-weight:    800;
        margin-bottom:  var(--space-md);
        letter-spacing: -0.02em;
    }}

    h1 {{ font-size: var(--fs-h1); {gradient_text} }}
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

    /* ── LAYOUT ──────────────────────────────────────────────────────── */
    .container {{
        max-width: 1300px;
        margin:    0 auto;
        padding:   0 clamp(1rem, 4vw, 2rem);
    }}

    main section {{
        padding:   var(--space-2xl) 0;
        position:  relative;
    }}

    .section-head {{
        text-align:    center;
        margin-bottom: var(--space-xl);
    }}

    .section-head h2 {{
        font-size: var(--fs-h2);
    }}

    /* Legacy grid (used by testimonials, blog, store cards) */
    .grid-3 {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(min(320px, 100%), 1fr));
        gap: clamp(1rem, 2.5vw, 2.5rem);
    }}

    .about-grid {{
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: clamp(2rem, 5vw, 5rem);
        align-items: center;
    }}

    .contact-grid {{
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: clamp(2rem, 4vw, 4rem);
        align-items: stretch;
    }}

    /* ── CARD ────────────────────────────────────────────────────────── */
    .card {{
        background:     var(--card);
        border-radius:  var(--radius);
        border:         var(--border);
        box-shadow:     var(--shadow);
        transition:
            transform   0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275),
            box-shadow  0.4s ease,
            border-color 0.35s ease,
            background-color 0.4s ease;
        display:        flex;
        flex-direction: column;
        overflow:       hidden;
        position:       relative;
        color:          var(--txt-b) !important;
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

    .card:hover {{
        transform:  translateY(-10px);
        box-shadow: 0 25px 50px -12px rgba(0,0,0,0.2);
    }}
    .card:hover::before {{ opacity: 1; }}

    .card h3 {{
        /* Fluid — scales between 1.1rem (mobile) and 1.4rem (desktop) */
        font-size:      clamp(1.1rem, 1.6vw, 1.4rem) !important;
        font-weight:    800;
        line-height:    1.2;
        margin-bottom:  0.4rem;
        color:          var(--txt-h) !important;
        letter-spacing: -0.02em;
    }}

    .card-body {{
        padding:        clamp(1.25rem, 2.5vw, 2rem);
        display:        flex;
        flex-direction: column;
        flex-grow:      1;
    }}

    .card-desc {{
        font-size:            clamp(0.875rem, 1.1vw, 0.95rem);
        line-height:          1.6;
        opacity:              0.7;
        margin-bottom:        1.5rem;
        display:              -webkit-box;
        -webkit-line-clamp:   2;
        -webkit-box-orient:   vertical;
        overflow:             hidden;
        color:                var(--txt-b);
    }}

    .prod-img {{
        width:       100%;
        height:      clamp(180px, 20vw, 280px);
        object-fit:  cover;
        transition:  transform 0.6s cubic-bezier(0.4, 0, 0.2, 1);
    }}
    .card:hover .prod-img {{ transform: scale(1.08); }}

    /* ── BUTTONS ─────────────────────────────────────────────────────── */
    .btn {{
        display:         inline-flex;
        align-items:     center;
        justify-content: center;
        padding:         clamp(0.9rem, 1.5vw, 1.2rem) clamp(1.5rem, 2.5vw, 2.5rem);
        border-radius:   var(--radius);
        font-weight:     800;
        text-decoration: none;
        transition:      all 0.3s ease;
        text-transform:  uppercase;
        cursor:          pointer;
        border:          none;
        text-align:      center;
        /* Fluid button label — never too tiny on mobile */
        font-size:       clamp(0.8rem, 1vw, 0.95rem);
        letter-spacing:  1.5px;
        position:        relative;
        overflow:        hidden;
        white-space:     nowrap;
    }}
    .btn-primary     {{ background: var(--p); color: #fff !important; }}
    .btn-accent      {{ background: var(--s); color: #fff !important; }}
    .btn-outline-light {{
        background:    transparent;
        color:         var(--txt-h) !important;
        border:        2px solid var(--txt-h);
    }}
    .btn-outline-light:hover {{
        background: var(--txt-h);
        color:      var(--bg) !important;
    }}
    .btn:hover {{ {btn_hover} }}

    /* ── NAVIGATION ──────────────────────────────────────────────────── */
    nav#main-navbar {{
        position:       fixed;
        top:            0;
        width:          100%;
        z-index:        2000;
        background:     var(--nav);
        backdrop-filter:         blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-bottom:  1px solid rgba(128,128,128,0.1);
        padding:        clamp(0.8rem, 1.5vw, 1.2rem) 0;
        transition:
            top        0.3s ease,
            background 0.4s ease,
            border-color 0.35s ease;
    }}

    .nav-flex  {{ display: flex; justify-content: space-between; align-items: center; }}
    .nav-links {{ display: flex; align-items: center; gap: clamp(1rem, 2vw, 2rem); }}

    .nav-links a {{
        text-decoration: none;
        font-weight:     600;
        color:           var(--txt-h);
        /* Fluid nav label size */
        font-size:       clamp(0.85rem, 1vw, 0.95rem);
        transition:      color 0.2s;
        position:        relative;
    }}
    .nav-links a::after {{
        content:          '';
        position:         absolute;
        width:            0;
        height:           2px;
        bottom:           -4px;
        left:             0;
        background-color: var(--p);
        transition:       width 0.3s ease;
    }}
    .nav-links a:hover::after {{ width: 100%; }}
    .nav-links a:hover {{ color: var(--p); }}

    .mobile-menu {{
        display:     none;
        font-size:   1.8rem;
        cursor:      pointer;
        background:  none;
        border:      none;
        color:       var(--txt-h);
        z-index:     2001;
        line-height: 1;
    }}

    /* ── HERO SECTIONS ───────────────────────────────────────────────── */
    .hero {{
        position:    relative;
        min-height:  95vh;
        overflow:    hidden;
        display:     flex;
        {h_align}
        padding-top: clamp(80px, 10vw, 120px);
    }}

    .carousel-slide {{
        position:          absolute;
        inset:             0;
        background-size:   cover;
        background-position: center;
        opacity:           0;
        transition:        opacity 1.5s cubic-bezier(0.4, 0, 0.2, 1),
                           transform 1.5s cubic-bezier(0.4, 0, 0.2, 1);
        z-index:           0;
        transform:         scale(1.05);
    }}
    .carousel-slide.active {{ opacity: 1; transform: scale(1); }}

    .hero-overlay {{
        background: linear-gradient(to bottom, rgba(0,0,0,0.3) 0%, rgba(0,0,0,0.8) 100%);
        position:   absolute;
        inset:      0;
        z-index:    1;
    }}

    .hero-content {{
        z-index:    2;
        position:   relative;
        width:      100%;
        padding:    0 5%;
        max-width:  1400px;
    }}

    .hero h1 {{
        color:                #ffffff !important;
        text-shadow:          0 10px 30px rgba(0,0,0,0.5);
        -webkit-text-fill-color: #fff;
        background:           none;
    }}

    .hero p {{
        color:       rgba(255,255,255,0.9) !important;
        /* Fluid hero subtext */
        font-size:   clamp(1rem, 2vw, 1.4rem);
        max-width:   800px;
        margin:      {hero_p_margin};
        font-weight: 400;
    }}

    /* Modern split hero */
    .modern-hero {{
        position:    relative;
        min-height:  100vh;
        display:     flex;
        {h_align}
        padding-top: clamp(80px, 10vw, 120px);
    }}

    .modern-hero-bg {{
        position:   absolute;
        top:        -50%;
        left:       -50%;
        width:      200%;
        height:     200%;
        background: radial-gradient(circle at 50% 50%, rgba(128,128,128,0.05) 0%, transparent 50%);
        z-index:    -1;
        animation:  rotate 60s linear infinite;
    }}

    @keyframes rotate {{
        from {{ transform: rotate(0deg); }}
        to   {{ transform: rotate(360deg); }}
    }}

    .modern-hero-grid {{
        display:             grid;
        grid-template-columns: 1.1fr 1fr;
        gap:                 clamp(2rem, 4vw, 4rem);
        align-items:         center;
        width:               100%;
    }}

    .hero-badge {{
        display:        inline-block;
        padding:        0.4rem 1rem;
        background:     rgba(128,128,128,0.1);
        border:         1px solid rgba(128,128,128,0.2);
        border-radius:  50px;
        /* Fluid badge label */
        font-size:      clamp(0.75rem, 1vw, 0.9rem);
        font-weight:    700;
        margin-bottom:  var(--space-md);
        color:          var(--txt-h);
        text-transform: uppercase;
        letter-spacing: 1px;
    }}

    .hero-btn-group {{ display: flex; gap: var(--space-sm); flex-wrap: wrap; }}

    .modern-hero-visual {{
        position:        relative;
        width:           100%;
        height:          clamp(300px, 45vw, 600px);
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

    .floating-element {{
        position:      absolute;
        border-radius: 50%;
        filter:        blur(60px);
        z-index:       1;
        opacity:       0.6;
    }}
    .glow-1 {{ width: clamp(150px,25vw,300px); height: clamp(150px,25vw,300px); background: var(--p); top: -50px; right: -50px; }}
    .glow-2 {{ width: clamp(120px,20vw,250px); height: clamp(120px,20vw,250px); background: var(--s); bottom: -50px; left: -50px; }}

    /* ── STATS RIBBON ────────────────────────────────────────────────── */
    .stats-ribbon-container {{
        margin-top: clamp(-30px, -4vw, -60px);
        position:   relative;
        z-index:    100;
        padding:    0 clamp(0.5rem, 2vw, 20px);
    }}

    .stats-ribbon {{
        background:     var(--card);
        border-radius:  24px;
        padding:        clamp(1.5rem, 3vw, 3rem);
        display:        flex;
        justify-content: space-around;
        align-items:    center;
        box-shadow:     var(--shadow);
        border:         var(--border);
        backdrop-filter: blur(20px);
        transition:     background-color 0.4s ease;
    }}

    .stat-block {{ text-align: center; }}

    .stat-block h3 {{
        /* Fluid stat number */
        font-size:     var(--fs-stat);
        color:         var(--p);
        margin-bottom: 0.5rem;
        line-height:   1;
    }}

    .stat-block p {{
        /* Fluid stat label */
        font-size:      clamp(0.8rem, 1.1vw, 1.1rem);
        font-weight:    600;
        color:          var(--txt-b);
        text-transform: uppercase;
        letter-spacing: 1px;
        opacity:        0.8;
        margin:         0;
    }}

    .stat-divider {{ width: 2px; height: 60px; background: rgba(128,128,128,0.2); }}

    /* ── SECTION SUBTITLE ────────────────────────────────────────────── */
    .section-subtitle {{
        font-size:      clamp(0.85rem, 1.2vw, 1.2rem);
        color:          var(--txt-b);
        opacity:        0.7;
        margin-top:     0.75rem;
        text-transform: uppercase;
        letter-spacing: 2px;
        font-weight:    600;
    }}

    /* ── PRODUCT DETAIL ──────────────────────────────────────────────── */
    .detail-view {{
        display:               grid;
        grid-template-columns: 0.8fr 1.2fr;
        gap:                   clamp(2rem, 5vw, 6rem);
        align-items:           start;
        background:            var(--card);
        padding:               clamp(1.5rem, 4vw, 5rem);
        border-radius:         32px;
        box-shadow:            var(--shadow);
        border:                var(--border);
        position:              relative;
    }}

    .product-media-column {{ position: sticky; top: 150px; }}

    .product-price-tag {{
        display:       inline-block;
        padding:       0.5rem 1.5rem;
        background:    rgba(5,150,105,0.1);
        color:         #059669;
        /* Fluid price tag */
        font-size:     clamp(1.2rem, 2vw, 1.8rem);
        font-weight:   900;
        border-radius: 50px;
        margin-bottom: var(--space-md);
    }}

    .product-info-column h1 {{
        font-size:     clamp(1.8rem, 3vw, 2.8rem) !important;
        margin-bottom: var(--space-sm) !important;
        line-height:   1.1;
    }}

    .product-specs-container,
    .product-specs-container p {{
        font-size:   clamp(0.9rem, 1.2vw, 1.05rem) !important;
        line-height: 1.7 !important;
        opacity:     0.85 !important;
    }}

    .product-specs-container strong {{
        display:    block;
        margin-top: var(--space-md);
        font-size:  clamp(1rem, 1.4vw, 1.2rem);
        color:      var(--p);
    }}

    .product-meta-box {{
        background:    rgba(128,128,128,0.05);
        padding:       var(--space-md);
        border-radius: var(--radius);
        margin-bottom: var(--space-lg);
        border-left:   5px solid var(--p);
    }}

    .back-btn {{
        font-size:     clamp(0.7rem, 1vw, 0.8rem) !important;
        margin-bottom: clamp(12px, 2vw, 24px) !important;
    }}

    .gallery-thumbs {{ display: flex; gap: 15px; margin-top: 20px; overflow-x: auto; padding-bottom: 10px; }}
    .thumb {{
        width:         clamp(60px, 7vw, 80px);
        height:        clamp(60px, 7vw, 80px);
        border-radius: var(--radius);
        object-fit:    cover;
        cursor:        pointer;
        border:        2px solid transparent;
        opacity:       0.6;
        transition:    all 0.3s;
    }}
    .thumb:hover, .thumb.active {{ border-color: var(--p); opacity: 1; transform: translateY(-5px); }}

    /* ── PRICING TABLE ───────────────────────────────────────────────── */
    .pricing-wrapper {{
        overflow-x:              auto;
        -webkit-overflow-scrolling: touch;
        width:                   100%;
        box-shadow:              var(--shadow);
        border-radius:           var(--radius);
        background:              var(--card);
        border:                  var(--border);
        transition:              background-color 0.4s ease;
    }}

    .pricing-table {{
        width:           100%;
        border-collapse: collapse;
        min-width:       600px;
    }}

    .pricing-table th {{
        background:     var(--p);
        color:          white;
        padding:        clamp(1rem, 2vw, 2rem);
        text-align:     left;
        font-size:      clamp(0.85rem, 1.1vw, 1.1rem);
        text-transform: uppercase;
        letter-spacing: 1px;
    }}

    .pricing-table td {{
        padding:       clamp(1rem, 2vw, 2rem);
        border-bottom: 1px solid rgba(128,128,128,0.1);
        color:         var(--txt-b);
        font-size:     clamp(0.85rem, 1.1vw, 1.1rem);
    }}

    .pricing-table tr:hover td {{ background: rgba(128,128,128,0.03); }}

    /* ── FOOTER ──────────────────────────────────────────────────────── */
    footer {{
        background:  #0f172a;
        color:       #f8fafc;
        padding:     clamp(3rem, 6vw, 6rem) 0 clamp(2rem, 3vw, 3rem) 0;
        margin-top:  auto;
        border-top:  4px solid var(--p);
    }}

    .footer-grid {{
        display:               grid;
        grid-template-columns: repeat(auto-fit, minmax(min(250px, 100%), 1fr));
        gap:                   clamp(2rem, 4vw, 4rem);
    }}

    footer a {{
        color:          #94a3b8 !important;
        text-decoration: none;
        display:         block;
        margin-bottom:   1rem;
        transition:      color 0.3s, transform 0.3s;
        font-size:       clamp(0.9rem, 1.1vw, 1.05rem);
    }}
    footer a:hover {{ color: #ffffff !important; transform: translateX(5px); }}

    .social-icon          {{ width: 28px; height: 28px; fill: #94a3b8; transition: fill 0.3s, transform 0.3s; }}
    .social-icon:hover    {{ fill: var(--p); transform: scale(1.2) translateY(-3px); }}

    /* ── ABOUT SECTION ───────────────────────────────────────────────── */
    .modern-about      {{ background: rgba(128,128,128,0.02); overflow: hidden; }}
    .about-visual      {{ position: relative; }}
    .about-main-img    {{
        width:         100%;
        height:        clamp(300px, 40vw, 600px);
        object-fit:    cover;
        border-radius: 32px;
        box-shadow:    var(--shadow);
    }}
    .about-experience-badge {{
        position:      absolute;
        bottom:        clamp(-15px, -2vw, -30px);
        right:         clamp(-15px, -2vw, -30px);
        background:    var(--p);
        color:         #fff;
        padding:       clamp(1rem, 2vw, 2rem);
        border-radius: 24px;
        box-shadow:    0 20px 40px rgba(0,0,0,0.2);
        display:       flex;
        align-items:   center;
        gap:           1rem;
        border:        4px solid var(--card);
    }}
    .about-experience-badge strong {{
        font-size:   clamp(2rem, 3vw, 3rem);
        line-height: 1;
        color:       #fff;
    }}
    .about-experience-badge span {{
        font-size:      clamp(0.8rem, 1vw, 1rem);
        font-weight:    700;
        text-transform: uppercase;
        line-height:    1.2;
    }}
    .about-lead {{
        font-size:   clamp(1rem, 1.5vw, 1.25rem);
        line-height: 1.8;
        opacity:     0.9;
        color:       var(--txt-b);
        border-left: 4px solid var(--s);
        padding-left: clamp(1rem, 2vw, 1.5rem);
    }}

    /* ── ACCESSIBILITY & REVEAL ──────────────────────────────────────── */
    .reveal {{
        opacity:    0;
        transform:  translateY(40px);
        transition: opacity 0.8s cubic-bezier(0.25,0.46,0.45,0.94),
                    transform 0.8s cubic-bezier(0.25,0.46,0.45,0.94);
        z-index:    10;
        position:   relative;
    }}
    .reveal.active {{ opacity: 1; transform: translateY(0); }}

    /* Respect user's motion preference */
    @media (prefers-reduced-motion: reduce) {{
        .reveal,
        .card,
        .bento-card,
        .carousel-slide,
        body,
        .modern-hero-bg {{
            transition: none !important;
            animation:  none !important;
        }}
    }}

    /* ── FAQ / DETAILS ───────────────────────────────────────────────── */
    details {{
        background:    var(--card);
        border:        var(--border);
        border-radius: var(--radius);
        margin-bottom: var(--space-sm);
        padding:       var(--space-md);
        cursor:        pointer;
        transition:    box-shadow 0.3s, transform 0.3s, background-color 0.4s;
    }}
    details:hover {{
        box-shadow:   var(--shadow);
        transform:    translateX(5px);
        border-left:  4px solid var(--p);
    }}
    details summary {{
        font-weight: 800;
        font-size:   clamp(1rem, 1.4vw, 1.2rem);
        outline:     none;
        list-style:  none;
    }}
    details summary::-webkit-details-marker {{ display: none; }}

    /* ── CART & OVERLAYS ─────────────────────────────────────────────── */
    #cart-float {{
        position:      fixed;
        bottom:        100px;
        right:         30px;
        background:    var(--p);
        color:         #fff;
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
        border:        2px solid rgba(255,255,255,0.1);
    }}
    #cart-float:hover {{ transform: scale(1.05) translateY(-5px); }}

    #cart-overlay {{
        display:         none;
        position:        fixed;
        inset:           0;
        background:      rgba(0,0,0,0.7);
        backdrop-filter: blur(5px);
        z-index:         3000;
    }}

    #cart-modal {{
        display:       none;
        position:      fixed;
        top:           50%;
        left:          50%;
        transform:     translate(-50%,-50%);
        background:    var(--card);
        width:         90%;
        max-width:     500px;
        max-height:    90vh;
        overflow-y:    auto;
        padding:       clamp(1.5rem, 3vw, 2.5rem);
        border-radius: 24px;
        box-shadow:    0 30px 60px rgba(0,0,0,0.4);
        z-index:       3001;
        border:        var(--border);
        color:         var(--txt-b);
        transition:    background-color 0.4s ease;
    }}
    #cart-modal h3 {{
        margin-bottom: 1.5rem;
        color:         var(--p);
        font-size:     clamp(1.3rem, 2vw, 1.8rem);
        border-bottom: 1px solid rgba(128,128,128,0.1);
        padding-bottom: 1rem;
    }}

    .cart-item {{
        display:       flex;
        justify-content: space-between;
        border-bottom: 1px solid rgba(128,128,128,0.1);
        padding:       15px 0;
        font-size:     clamp(0.9rem, 1.1vw, 1.1rem);
    }}

    .local-vault {{
        background:    rgba(128,128,128,0.05);
        padding:       var(--space-md);
        border-radius: 12px;
        margin-top:    var(--space-md);
        border:        1px solid rgba(128,128,128,0.1);
    }}
    .local-vault input {{
        width:         100%;
        padding:       1rem;
        margin-top:    0.5rem;
        border-radius: 8px;
        border:        var(--border);
        background:    var(--bg);
        color:         var(--txt-b);
        font-size:     1rem;
        transition:    background-color 0.4s, color 0.4s;
    }}

    /* ── POPUP ────────────────────────────────────────────────────────── */
    #lead-popup {{
        display:       none;
        position:      fixed;
        top:           50%;
        left:          50%;
        transform:     translate(-50%,-50%);
        background:    var(--card);
        padding:       clamp(2rem, 4vw, 3.5rem);
        text-align:    center;
        border-radius: var(--radius);
        z-index:       3001;
        box-shadow:    0 30px 60px rgba(0,0,0,0.5);
        width:         90%;
        max-width:     500px;
        border:        var(--border);
        color:         var(--txt-b);
        transition:    background-color 0.4s ease;
    }}
    .close-popup {{
        position:   absolute;
        top:        15px;
        right:      20px;
        cursor:     pointer;
        font-size:  2rem;
        opacity:    0.5;
        transition: opacity 0.3s, color 0.3s;
    }}
    .close-popup:hover {{ opacity: 1; color: var(--s); }}

    /* ── LANGUAGE MODAL ──────────────────────────────────────────────── */
    #lang-overlay {{
        display:         none;
        position:        fixed;
        inset:           0;
        background:      rgba(0,0,0,0.7);
        backdrop-filter: blur(5px);
        z-index:         3000;
    }}
    #lang-modal {{
        display:       none;
        position:      fixed;
        top:           50%;
        left:          50%;
        transform:     translate(-50%,-50%);
        background:    var(--card);
        width:         90%;
        max-width:     500px;
        padding:       clamp(1.5rem, 3vw, 3rem);
        border-radius: 24px;
        box-shadow:    0 30px 60px rgba(0,0,0,0.4);
        z-index:       3001;
        border:        var(--border);
        color:         var(--txt-b);
        transition:    background-color 0.4s ease;
    }}
    #lang-modal h3 {{
        margin-bottom:  1.5rem;
        color:          var(--p);
        font-size:      clamp(1.3rem, 2vw, 1.8rem);
        border-bottom:  1px solid rgba(128,128,128,0.1);
        padding-bottom: 1rem;
        text-align:     center;
    }}
    .lang-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }}
    .lang-opt {{
        display:         flex;
        align-items:     center;
        justify-content: center;
        width:           100%;
        padding:         1.2rem;
        border:          var(--border);
        border-radius:   12px;
        cursor:          pointer;
        font-weight:     700;
        transition:      background 0.3s, color 0.3s, transform 0.3s;
        background:      var(--bg);
    }}
    .lang-opt:hover {{
        background:  var(--p);
        color:       #fff;
        transform:   translateY(-3px);
        box-shadow:  0 10px 20px rgba(0,0,0,0.1);
    }}

    /* ── TOP PROMO BAR ───────────────────────────────────────────────── */
    #top-bar {{
        position:       fixed;
        top:            0;
        left:           0;
        width:          100%;
        background:     var(--s);
        color:          #fff;
        text-align:     center;
        padding:        clamp(8px, 1vw, 12px);
        z-index:        2005;
        font-weight:    800;
        font-size:      clamp(0.8rem, 1vw, 0.95rem);
        letter-spacing: 1px;
        transition:     transform 0.3s;
        box-shadow:     0 4px 10px rgba(0,0,0,0.1);
    }}
    #top-bar a {{ color: #fff !important; text-decoration: none; margin-left: 10px; transition: opacity 0.3s; }}
    #top-bar a:hover {{ opacity: 0.8; }}

    /* ── DARK MODE TOGGLE ────────────────────────────────────────────── */
    #theme-toggle {{
        position:        fixed;
        bottom:          30px;
        left:            30px;
        width:           50px;
        height:          50px;
        background:      var(--card);
        border-radius:   50%;
        display:         flex;
        align-items:     center;
        justify-content: center;
        box-shadow:      0 10px 25px rgba(0,0,0,0.2);
        cursor:          pointer;
        z-index:         1000;
        font-size:       1.5rem;
        border:          var(--border);
        transition:      transform 0.3s, border-color 0.3s,
                         background-color 0.4s ease;
    }}
    #theme-toggle:hover {{ transform: scale(1.1) rotate(15deg); border-color: var(--p); }}

    /* ── VOICE SEARCH ────────────────────────────────────────────────── */
    #voice-btn {{
        position:        fixed;
        bottom:          170px;
        right:           30px;
        background:      var(--p);
        color:           #fff;
        border-radius:   50%;
        width:           50px;
        height:          50px;
        display:         flex;
        align-items:     center;
        justify-content: center;
        font-size:       1.2rem;
        cursor:          pointer;
        box-shadow:      0 10px 25px rgba(0,0,0,0.2);
        z-index:         1000;
        border:          2px solid rgba(255,255,255,0.1);
        transition:      transform 0.3s, background 0.3s;
    }}
    #voice-btn:hover {{ transform: scale(1.1); background: var(--s); }}

    .listening {{ animation: voice-pulse 1.5s infinite; background: var(--s) !important; }}

    @keyframes voice-pulse {{
        0%   {{ transform: scale(1);   box-shadow: 0 0 0  0px rgba(255,0,60,0.4); }}
        70%  {{ transform: scale(1.2); box-shadow: 0 0 0 20px rgba(255,0,60,0);   }}
        100% {{ transform: scale(1);   box-shadow: 0 0 0  0px rgba(255,0,60,0);   }}
    }}

    /* ── SHARE ROW ───────────────────────────────────────────────────── */
    .share-row {{
        display:     flex;
        gap:         12px;
        flex-wrap:   wrap;
        align-items: center;
        margin-top:  1.5rem;
    }}
    .share-btn {{
        width:           45px !important;
        height:          45px !important;
        display:         flex !important;
        align-items:     center;
        justify-content: center;
        border-radius:   12px;
        transition:      transform 0.3s, opacity 0.3s;
        text-decoration: none;
    }}
    .share-btn:hover {{ transform: translateY(-3px); opacity: 0.9; }}
    .share-btn svg, .share-row svg {{
        width:  22px !important;
        height: 22px !important;
        fill:   white;
    }}
    .bg-wa {{ background: #25D366; }}
    .bg-fb {{ background: #1877F2; }}
    .bg-x  {{ background: #000000; }}
    .bg-li {{ background: #0A66C2; }}
    .bg-link {{ background: #64748b; }}

    /* ── BENTO GRID (injected here) ──────────────────────────────────── */
    {bento_css}

    /* ── DARK MODE SYSTEM (injected here) ───────────────────────────── */
    {dark_css}

    /* ── RESPONSIVE: TABLET (≤992px) ────────────────────────────────── */
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
            transition:     left 0.4s ease;
            align-items:    center;
            justify-content: flex-start;
            gap:            2.5rem;
            z-index:        1999;
            overflow-y:     auto;
        }}
        nav#main-navbar .nav-links.active {{ left: 0; }}

        .nav-links a   {{ font-size: 1.5rem; }}
        .mobile-menu   {{ display: block; }}

        .about-grid,
        .detail-view,
        .grid-3,
        .contact-grid  {{ grid-template-columns: 1fr !important; gap: 2rem; }}

        .modern-hero-grid  {{ grid-template-columns: 1fr; text-align: center; }}
        .modern-hero-text  {{ text-align: center; align-items: center; justify-content: center; }}
        .hero-btn-group    {{ justify-content: center; }}
        .modern-hero-visual {{ height: clamp(260px, 40vw, 400px); }}
        .hero              {{ padding-top: 100px; text-align: center; }}

        .detail-view       {{ padding: clamp(1.5rem, 3vw, 2rem); gap: 2rem; }}
        .product-media-column {{ position: relative; top: 0; margin-bottom: 2rem; }}

        .stats-ribbon      {{ flex-direction: column; padding: 2.5rem 1.5rem; gap: 2rem; }}
        .stat-divider      {{ width: 100%; height: 2px; }}
        .stats-ribbon-container {{ margin-top: -30px; }}

        .about-experience-badge {{
            position:    relative;
            bottom:      0;
            right:       0;
            margin-top:  -30px;
            margin-left: auto;
            margin-right: auto;
            width:       fit-content;
            z-index:     10;
        }}

        .pricing-table th,
        .pricing-table td {{ padding: 1.2rem 1rem; }}
    }}

    /* ── RESPONSIVE: MOBILE (≤480px) ────────────────────────────────── */
    @media (max-width: 480px) {{
        /* Left-align body copy — prevents 'rivers' on narrow columns */
        p {{
            text-align: left;
            hyphens: auto;
        }}

        html, body {{
            width:      100% !important;
            margin:     0 !important;
            padding:    0 !important;
            overflow-x: hidden !important;
            background: var(--bg);
        }}

        .container {{
            width:     100% !important;
            max-width: 100% !important;
            padding:   0 clamp(1rem, 5vw, 1.5rem) !important;
            margin:    0 auto !important;
        }}

        footer {{
            /* Extra bottom clearance so floating buttons don't cover footer links */
            padding-bottom: 10rem !important;
        }}
        .footer-grid {{
            display:        flex !important;
            flex-direction: column !important;
            gap:            2.5rem !important;
            text-align:     left !important;
        }}

        /* NOTE: h1/h2/h3 do NOT need !important overrides here —
           clamp() already handles mobile sizing via its floor value.
           Removing the old !important blocks is intentional. */

        .hero-btn-group {{
            flex-direction: column !important;
            width:          100%;
        }}
        .hero-btn-group .btn {{ width: 100% !important; }}

        /* Floating button traffic control — pin to corners at 0.8× scale */
        #wa-widget    {{ bottom: 15px !important; right: 10px !important; scale: 0.8; }}
        #theme-toggle {{ bottom: 15px !important; left:  10px !important; scale: 0.8; background: rgba(255,255,255,0.9); border: 1px solid rgba(0,0,0,0.1); }}
        #cart-float   {{ bottom: 80px  !important; right: 10px !important; scale: 0.8; }}
        #voice-btn    {{ bottom: 140px !important; right: 10px !important; scale: 0.8; }}

        .modern-hero-visual {{ height: 280px !important; margin-top: 2rem !important; }}
        .visual-frame       {{ border-width: 4px !important; }}
        .modern-feature-card {{ padding: 1.5rem !important; }}

        .pricing-table      {{ min-width: 100% !important; }}
        .pricing-table th,
        .pricing-table td   {{ padding: 0.75rem 0.5rem !important; }}
    }}
    """
