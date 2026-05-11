# utils.py  — Titan Engine v56 "Flawless"
# Zero-dependency helper functions.
# Importable by any Titan module. Never import from compiler, templates, or titan_themes here.

import re
import html as html_lib


# ---------------------------------------------------------------------------
# 1. INPUT SANITISATION
# ---------------------------------------------------------------------------

def sanitize(text: str, for_js: bool = False) -> str:
    """
    Sanitize user-supplied text before injecting into generated HTML or JS.

    Why this matters:
      - Newlines inside JS string literals cause "Unterminated string constant".
      - Unescaped < / > / & in HTML content create broken markup or XSS vectors.
      - Apostrophes inside onclick='...' attributes terminate the attribute early.

    Args:
        text:    Raw user input (from an st.text_input / st.text_area).
        for_js:  If True, also escape single/double quotes for safe JS string embedding.

    Returns:
        A string safe to embed in an HTML attribute or a JS string literal.
    """
    if not text:
        return ""
    # 1. Collapse all newline variants into a single space
    safe = text.replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ')
    # 2. Escape HTML special characters
    safe = safe.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    # 3. If the value will appear inside a JS string literal, escape quotes too
    if for_js:
        safe = safe.replace("'", "\\'").replace('"', '\\"')
    return safe


def sanitize_url(url: str) -> str:
    """
    Ensure a URL is safe to inject into href / src attributes.
    Strips leading/trailing whitespace and rejects javascript: pseudo-protocol.
    Also rejects data: URIs that could embed scripts.
    """
    url = url.strip()
    lower = url.lower()
    if lower.startswith('javascript:') or lower.startswith('data:text/html'):
        return '#'
    return url


def sanitize_embed(html_str: str) -> str:
    """
    Light sanitization for user-supplied embed codes (map iframes, booking widgets).
    Strips javascript: protocol from src attributes and removes <script> tags
    that aren't from known safe CDNs. Allows Calendly and Google iframes.
    """
    if not html_str:
        return ""
    # Remove script tags that are NOT from trusted CDNs
    safe = re.sub(
        r'<script(?!\s+src=["\']https://(assets\.calendly\.com|maps\.googleapis\.com))[^>]*>.*?</script>',
        '',
        html_str,
        flags=re.IGNORECASE | re.DOTALL,
    )
    # Strip javascript: src values
    safe = re.sub(r'src=["\']javascript:[^"\']*["\']', 'src="#"', safe, flags=re.IGNORECASE)
    return safe


# ---------------------------------------------------------------------------
# 2. CONTRAST & COLOUR UTILITIES
# ---------------------------------------------------------------------------

def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """Convert a hex colour string (#RRGGBB or #RGB) to an (R, G, B) tuple."""
    h = hex_color.strip().lstrip('#')
    if len(h) == 3:
        h = ''.join(c * 2 for c in h)
    if len(h) != 6:
        return (0, 0, 0)
    try:
        return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))
    except ValueError:
        return (0, 0, 0)


def _relative_luminance(r: int, g: int, b: int) -> float:
    """
    Calculate relative luminance per WCAG 2.1 formula.
    Returns a value in [0, 1] where 0 = black and 1 = white.
    """
    def linearise(c: int) -> float:
        s = c / 255.0
        return s / 12.92 if s <= 0.04045 else ((s + 0.055) / 1.055) ** 2.4

    return 0.2126 * linearise(r) + 0.7152 * linearise(g) + 0.0722 * linearise(b)


def contrast_ratio(hex_a: str, hex_b: str) -> float:
    """
    WCAG 2.1 contrast ratio between two hex colours.
    Returns a value in [1, 21]. WCAG AA large text = 3.0, normal text = 4.5.
    """
    la = _relative_luminance(*_hex_to_rgb(hex_a))
    lb = _relative_luminance(*_hex_to_rgb(hex_b))
    lighter, darker = max(la, lb), min(la, lb)
    return (lighter + 0.05) / (darker + 0.05)


def accessible_text_color(bg_hex: str, dark: str = "#0f172a", light: str = "#ffffff") -> str:
    """
    Given a background colour, return whichever of `dark` or `light`
    achieves the better WCAG contrast ratio against it.

    Usage in titan_themes.py:
        btn_text = accessible_text_color(theme['p'])
    This guarantees readable button labels no matter what accent colour the user picks.
    """
    ratio_dark  = contrast_ratio(bg_hex, dark)
    ratio_light = contrast_ratio(bg_hex, light)
    return dark if ratio_dark >= ratio_light else light


def darken_hex(hex_color: str, factor: float = 0.15) -> str:
    """
    Darken a hex colour by multiplying each channel by (1 - factor).
    Used to generate hover states programmatically without requiring
    a preprocessor.

    Args:
        hex_color:  Source colour in #RRGGBB format.
        factor:     How much to darken (0.0 = no change, 1.0 = black).
    Returns:
        Darkened colour in #RRGGBB format.
    """
    r, g, b = _hex_to_rgb(hex_color)
    f = 1.0 - max(0.0, min(1.0, factor))
    return '#{:02x}{:02x}{:02x}'.format(int(r * f), int(g * f), int(b * f))


def alpha_hex(hex_color: str, alpha: float = 0.1) -> str:
    """
    Convert a hex colour + alpha float to an rgba() CSS string.
    Avoids the browser compatibility issues of #RRGGBBAA.

    Example: alpha_hex('#ef4444', 0.15) → 'rgba(239,68,68,0.15)'
    """
    r, g, b = _hex_to_rgb(hex_color)
    return f'rgba({r},{g},{b},{alpha})'


# ---------------------------------------------------------------------------
# 3. MARKDOWN → HTML FORMATTER  (for long-form body copy)
# ---------------------------------------------------------------------------

def format_text(text: str) -> str:
    """
    Convert a lightweight subset of Markdown to HTML paragraphs and lists.
    Handles: **bold**, * bullet lists, plain paragraphs.
    Used for: about_long, priv_txt, term_txt — fields rendered in <section> bodies.

    v56 CHANGE: Uses html.escape() as a first pass instead of manual replacement
    to catch edge cases like bare ampersands in URLs.
    """
    if not text:
        return ""
    escaped = html_lib.escape(text)
    processed = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', escaped)
    lines = processed.split('\n')
    html_out = ""
    in_list = False
    for line in lines:
        clean = line.strip()
        if not clean:
            if in_list:
                html_out += "</ul>"
                in_list = False
            continue
        if clean.startswith("* "):
            if not in_list:
                html_out += '<ul style="margin-bottom:1rem; padding-left:1.5rem;">'
                in_list = True
            html_out += f'<li style="margin-bottom:0.5rem; opacity:0.9; color:inherit;">{clean[2:]}</li>'
        else:
            if in_list:
                html_out += "</ul>"
                in_list = False
            html_out += f"<p style='margin-bottom:1rem; opacity:0.9; color:inherit;'>{clean}</p>"
    if in_list:
        html_out += "</ul>"
    return html_out


# ---------------------------------------------------------------------------
# 4. ICON HELPER
# ---------------------------------------------------------------------------

_ICON_MAP: dict[str, str] = {
    "bolt":    "M11 21h-1l1-7H7.5c-.58 0-.57-.32-.38-.66.19-.34.05-.08.07-.12C8.48 10.94 10.42 7.54 13 3h1l-1 7h3.5c.49 0 .56.33.47.51l-.07.15C12.96 17.55 11 21 11 21z",
    "wallet":  "M21 18v1c0 1.1-.9 2-2 2H5c-1.11 0-2-.9-2-2V5c0-1.1.89-2 2-2h14c1.1 0 2 .9 2 2v1h-9c-1.11 0-2 .9-2 2v8c0 1.1.89 2 2 2h9zm-9-2h10V8H12v8zm4-2.5c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5z",
    "table":   "M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zM5 19V5h14v14H5zm2-2h10v-2H7v2zm0-4h10v-2H7v2zm0-4h10V7H7v2z",
    "shield":  "M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4zm0 10.99h7c-.53 4.12-3.28 7.79-7 8.94V12H5V6.3l7-3.11v8.8z",
    "layers":  "M11.99 18.54l-7.37-5.73L3 14.07l9 7 9-7-1.63-1.27-7.38 5.74zM12 16l7.36-5.73L21 9l-9-7-9 7 1.63 1.27L12 16z",
    "star":    "M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z",
    "chart":   "M3.5 18.49l6-6.01 4 4L22 6.92l-1.41-1.41-7.09 7.97-4-4L2 16.99z",
    "globe":   "M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z",
    "lock":    "M18 8h-1V6c0-2.76-2.24-5-5-5S7 3.24 7 6v2H6c-1.1 0-2 .9-2 2v10c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V10c0-1.1-.9-2-2-2zm-6 9c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2zm3.1-9H8.9V6c0-1.71 1.39-3.1 3.1-3.1 1.71 0 3.1 1.39 3.1 3.1v2z",
    "check":   "M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z",
    "zap":     "M11 21h-1l1-7H7.5c-.58 0-.57-.32-.38-.66.19-.34.05-.08.07-.12C8.48 10.94 10.42 7.54 13 3h1l-1 7h3.5c.49 0 .56.33.47.51l-.07.15C12.96 17.55 11 21 11 21z",
    "users":   "M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z",
    "award":   "M19 5h-2V3H7v2H5c-1.1 0-2 .9-2 2v1c0 2.55 1.92 4.63 4.39 4.94.63 1.5 1.98 2.63 3.61 2.96V18H7v2h10v-2h-4v-2.1c1.63-.33 2.98-1.46 3.61-2.96C19.08 12.63 21 10.55 21 8V7c0-1.1-.9-2-2-2zM5 8V7h2v3.82C5.84 10.4 5 9.3 5 8zm14 0c0 1.3-.84 2.4-2 2.82V7h2v1z",
}
_ICON_FALLBACK = "M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"


def get_simple_icon(name: str) -> str:
    """Return an inline SVG icon by keyword name. Falls back to a checkmark."""
    path = _ICON_MAP.get(name.lower().strip(), _ICON_FALLBACK)
    return f'<svg viewBox="0 0 24 24" width="32" height="32" fill="currentColor" aria-hidden="true" focusable="false"><path d="{path}"/></svg>'


# ---------------------------------------------------------------------------
# 5. YOUTUBE ID EXTRACTOR
# ---------------------------------------------------------------------------

def extract_youtube_id(raw: str) -> str:
    """
    Extract a clean 11-character YouTube video ID from any YouTube URL format
    or a raw ID string. Handles: ?v=, /embed/, youtu.be/, /shorts/, raw IDs.
    """
    raw = raw.strip()
    match = re.search(
        r'(?:v=|/v/|youtu\.be/|/embed/|/shorts/|^)([a-zA-Z0-9_-]{11})',
        raw
    )
    return match.group(1) if match else raw


# ---------------------------------------------------------------------------
# 6. PHONE / WHATSAPP NORMALISER
# ---------------------------------------------------------------------------

def clean_phone(raw: str) -> str:
    """Strip +, spaces, and dashes from a phone number for use in wa.me/ links."""
    return re.sub(r'[^\d]', '', raw)


# ---------------------------------------------------------------------------
# 7. CSS VALUE HELPERS
# ---------------------------------------------------------------------------

def css_var(name: str) -> str:
    """Emit a CSS var() reference. Use to reduce typos: css_var('--p') → 'var(--p)'"""
    return f'var({name})'


def rem(value: float) -> str:
    """Format a float as a rem CSS value string."""
    return f'{value}rem'
