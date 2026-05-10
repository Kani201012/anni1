# utils.py
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
    """
    url = url.strip()
    if url.lower().startswith('javascript:'):
        return '#'
    return url


# ---------------------------------------------------------------------------
# 2. MARKDOWN → HTML FORMATTER  (for long-form body copy)
# ---------------------------------------------------------------------------

def format_text(text: str) -> str:
    """
    Convert a lightweight subset of Markdown to HTML paragraphs and lists.
    Handles: **bold**, * bullet lists, plain paragraphs.
    Used for: about_long, priv_txt, term_txt — fields rendered in <section> bodies.
    """
    if not text:
        return ""
    processed = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    lines = processed.split('\n')
    html_out = ""
    in_list = False
    for line in lines:
        clean = line.strip()
        if not clean:
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
# 3. ICON HELPER
# ---------------------------------------------------------------------------

_ICON_MAP: dict[str, str] = {
    "bolt":    "M11 21h-1l1-7H7.5c-.58 0-.57-.32-.38-.66.19-.34.05-.08.07-.12C8.48 10.94 10.42 7.54 13 3h1l-1 7h3.5c.49 0 .56.33.47.51l-.07.15C12.96 17.55 11 21 11 21z",
    "wallet":  "M21 18v1c0 1.1-.9 2-2 2H5c-1.11 0-2-.9-2-2V5c0-1.1.89-2 2-2h14c1.1 0 2 .9 2 2v1h-9c-1.11 0-2 .9-2 2v8c0 1.1.89 2 2 2h9zm-9-2h10V8H12v8zm4-2.5c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5z",
    "table":   "M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zM5 19V5h14v14H5zm2-2h10v-2H7v2zm0-4h10v-2H7v2zm0-4h10V7H7v2z",
    "shield":  "M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4zm0 10.99h7c-.53 4.12-3.28 7.79-7 8.94V12H5V6.3l7-3.11v8.8z",
    "layers":  "M11.99 18.54l-7.37-5.73L3 14.07l9 7 9-7-1.63-1.27-7.38 5.74zM12 16l7.36-5.73L21 9l-9-7-9 7 1.63 1.27L12 16z",
    "star":    "M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z",
}
_ICON_FALLBACK = "M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"


def get_simple_icon(name: str) -> str:
    """Return an inline SVG icon by keyword name. Falls back to a checkmark."""
    path = _ICON_MAP.get(name.lower().strip(), _ICON_FALLBACK)
    return f'<svg viewBox="0 0 24 24" width="32" height="32" fill="currentColor"><path d="{path}"/></svg>'


# ---------------------------------------------------------------------------
# 4. YOUTUBE ID EXTRACTOR
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
# 5. PHONE / WHATSAPP NORMALISER
# ---------------------------------------------------------------------------

def clean_phone(raw: str) -> str:
    """Strip +, spaces, and dashes from a phone number for use in wa.me/ links."""
    return raw.replace('+', '').replace(' ', '').replace('-', '')
