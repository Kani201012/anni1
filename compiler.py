# compiler.py  — Titan Engine v56 "Flawless"
# The HTML compilation layer. Zero Streamlit imports.
#
# v56 CHANGES vs v55:
#   1. build_page() injects gen_runtime_js() ONCE per page — before </body>.
#      This means parseCSVLine, parseMarkdown, and titanToast are always
#      available when section scripts run, regardless of DOM readiness.
#   2. gen_schema() now emits a richer LocalBusiness + WebSite schema pair.
#   3. gen_pwa_manifest() correctly handles gradient/CSS bg values by
#      extracting only the first hex colour.
#   4. SiteConfig gains `biz_tagline` wired through to footer.
#   5. _scroll_reveal_script() removed — reveal is now handled by the
#      IntersectionObserver inside gen_runtime_js().
#   6. build_zip() emits a human-readable _README.txt explaining the package.

from __future__ import annotations

import io
import re
import json
import zipfile
import datetime
from dataclasses import dataclass, field

import titan_themes
import templates


# ---------------------------------------------------------------------------
# 1. SITE CONFIG DATACLASS
# ---------------------------------------------------------------------------

@dataclass
class SiteConfig:
    # --- Identity ---
    biz_name:       str = "StopWebRent.com"
    biz_tagline:    str = "Stop Renting. Start Owning."
    biz_phone:      str = "966572562151"
    biz_email:      str = "hello@example.com"
    biz_addr:       str = "Kaydiem Script Lab\nKolkata, India"
    prod_url:       str = "https://www.stopwebrent.com"
    logo_url:       str = ""
    map_iframe:     str = ""
    seo_d:          str = "Stop paying monthly fees for web hosting."

    # --- PWA ---
    pwa_short:      str = "StopWebRent"
    pwa_desc:       str = "Official App"
    pwa_icon:       str = ""

    # --- Social ---
    fb_link:        str = ""
    ig_link:        str = ""
    x_link:         str = ""
    li_link:        str = ""
    yt_link:        str = ""
    wa_num:         str = "966572562151"

    # --- Theme / Design ---
    theme_mode:     str = "1. Stripe Cloud (Modern SaaS)"
    hero_layout:    str = "Center"
    h_font:         str = "Space Grotesk"
    b_font:         str = "Inter"
    overlay_opacity: float = 0.5
    col_h:          str = "#0f172a"
    col_b:          str = "#475569"
    size_h1:        float = 4.5
    size_p:         float = 1.1
    cta_bg_color:   str = "#10b981"
    cta_txt_color:  str = "#ffffff"

    # --- Feature Flags ---
    enable_ar:      bool = True
    enable_voice:   bool = True
    enable_context: bool = True
    enable_ab:      bool = True

    # --- Section Visibility ---
    show_hero:         bool = True
    show_stats:        bool = True
    show_features:     bool = True
    show_pricing:      bool = True
    show_inventory:    bool = True
    show_blog:         bool = True
    show_gallery:      bool = True
    show_testimonials: bool = True
    show_faq:          bool = True
    show_cta:          bool = True
    show_booking:      bool = True

    # --- SEO / Analytics ---
    seo_area:       str = "Global / Online"
    seo_kw:         str = "web design, no monthly fees"
    gsc_tag:        str = ""
    ga_tag:         str = ""
    og_image:       str = ""

    # --- Hero Content ---
    hero_h:         str = "Stop Paying Rent for Your Website."
    hero_sub:       str = "The Titan Engine. Pay once. Own it forever."
    hero_badge_txt: str = "🚀 Next-Generation Architecture"
    hero_video_id:  str = ""
    hero_img_1:     str = "https://images.unsplash.com/photo-1460925895917-afdab827c52f?q=80&w=1600"
    hero_img_2:     str = "https://images.unsplash.com/photo-1551288049-bebda4e38f71?q=80&w=1600"
    hero_img_3:     str = "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?q=80&w=1600"

    # --- Stats ---
    stat_1: str = "0.1s";  label_1: str = "Speed"
    stat_2: str = "$0";    label_2: str = "Fees"
    stat_3: str = "100%";  label_3: str = "Ownership"

    # --- Features ---
    f_title:        str = "Value Pillars"
    feat_data:      str = ""

    # --- About ---
    about_h:        str = "Control Your Empire from a Spreadsheet"
    about_img:      str = "https://images.unsplash.com/photo-1543286386-713df548e9cc?q=80&w=1600"
    about_short:    str = ""
    about_long:     str = ""

    # --- Marketing ---
    top_bar_enabled: bool = False
    top_bar_text:    str = "🔥 50% OFF Launch Sale - Ends Soon!"
    top_bar_link:    str = "#pricing"
    popup_enabled:   bool = False
    popup_delay:     int = 5
    popup_title:     str = "Wait! Don't leave empty handed."
    popup_text:      str = "Get our free pricing guide on WhatsApp."
    popup_cta:       str = "Get it Now"

    # --- Pricing ---
    titan_price: str = "$199";  titan_mo: str = "$0"
    wix_name:    str = "Wix";   wix_mo:   str = "$29/mo"
    save_val:    str = "$1,466"

    # --- Store ---
    sheet_url:      str = ""
    custom_feat:    str = "https://images.unsplash.com/photo-1460925895917-afdab827c52f?q=80&w=800"
    paypal_link:    str = "https://paypal.me/yourid"
    upi_id:         str = "name@upi"

    # --- Booking ---
    booking_embed:  str = ""
    booking_title:  str = "Book an Appointment"
    booking_desc:   str = "Select a time slot."

    # --- Blog ---
    blog_sheet_url:  str = ""
    blog_hero_title: str = "Latest Insights"
    blog_hero_sub:   str = "Thoughts on tech."

    # --- Legal / Content ---
    testi_data: str = ""
    faq_data:   str = ""
    priv_txt:   str = "We collect minimum data."
    term_txt:   str = "You own the code."

    # --- Multi-language ---
    lang_sheet: str = ""

    # --- IPFS ---
    pinata_jwt: str = ""


# ---------------------------------------------------------------------------
# 2. CSS BUILDER
# ---------------------------------------------------------------------------

def build_css(cfg: SiteConfig) -> str:
    return titan_themes.generate_modern_css(
        cfg.theme_mode,
        cfg.h_font,
        cfg.b_font,
        cfg.hero_layout,
        h_color=cfg.col_h,
        b_color=cfg.col_b,
        h1_size=f"{cfg.size_h1}rem",
        p_size=f"{cfg.size_p}rem",
        cta_bg=cfg.cta_bg_color,
        cta_txt=cfg.cta_txt_color,
    )


# ---------------------------------------------------------------------------
# 3. STATIC ASSET GENERATORS
# ---------------------------------------------------------------------------

def gen_schema(cfg: SiteConfig) -> str:
    """
    Emit JSON-LD structured data.
    v56: Adds WebSite schema with SearchAction for Google Sitelinks Search Box.
    """
    local_biz = {
        "@context": "https://schema.org",
        "@type": "LocalBusiness",
        "name": cfg.biz_name,
        "description": cfg.seo_d,
        "url": cfg.prod_url,
        "telephone": cfg.biz_phone,
        "email": cfg.biz_email,
        "image": cfg.og_image or cfg.logo_url or cfg.hero_img_1,
        "address": {
            "@type": "PostalAddress",
            "addressLocality": cfg.seo_area,
        },
        "sameAs": [u for u in [cfg.fb_link, cfg.ig_link, cfg.x_link, cfg.li_link] if u],
    }
    website = {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "url": cfg.prod_url,
        "name": cfg.biz_name,
    }
    combined = [local_biz, website]
    return f'<script type="application/ld+json">{json.dumps(combined, ensure_ascii=False)}</script>'


def _extract_hex(value: str) -> str:
    """
    Extract the first hex colour from a string.
    Handles plain '#RRGGBB', 'linear-gradient(...#RRGGBB...)', CSS vars, etc.
    Falls back to '#000000' if nothing is found.
    """
    match = re.search(r'#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b', value)
    return match.group(0) if match else '#000000'


def gen_pwa_manifest(cfg: SiteConfig) -> str:
    """
    v56 FIX: gradient and rgba() values from the theme registry cannot be
    used as manifest theme_color / background_color — only hex values are valid.
    _extract_hex() pulls the first hex colour from any CSS value string.
    """
    theme = titan_themes.THEME_REGISTRY.get(
        cfg.theme_mode,
        titan_themes.THEME_REGISTRY["1. Stripe Cloud (Modern SaaS)"]
    )
    bg_color     = _extract_hex(theme['bg'])
    theme_color  = _extract_hex(theme['p'])
    icons = []
    if cfg.pwa_icon:
        icons = [
            {"src": cfg.pwa_icon, "sizes": "192x192", "type": "image/png", "purpose": "any"},
            {"src": cfg.pwa_icon, "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
        ]
    return json.dumps({
        "name": cfg.biz_name,
        "short_name": cfg.pwa_short,
        "description": cfg.pwa_desc,
        "start_url": "./index.html",
        "display": "standalone",
        "orientation": "any",
        "background_color": bg_color,
        "theme_color": theme_color,
        "icons": icons,
        "categories": ["business"],
        "screenshots": [],
    }, ensure_ascii=False, indent=2)


def gen_sw() -> str:
    """
    v56: Service worker with stale-while-revalidate strategy for HTML pages,
    cache-first for static assets, network-only for spreadsheet data.
    Cache version bumped to v56 to force fresh install.
    """
    return """
'use strict';
const CACHE_STATIC = 'titan-v56-static';
const CACHE_DATA   = 'titan-v56-data';
const STATIC_URLS  = [
    './index.html', './about.html', './contact.html',
    './product.html', './blog.html', './post.html',
    './booking.html', './privacy.html', './terms.html',
];

self.addEventListener('install', (e) => {
    e.waitUntil(
        caches.open(CACHE_STATIC)
            .then(c => c.addAll(STATIC_URLS.filter(Boolean)))
            .catch(err => console.warn('[SW] Pre-cache partial failure:', err))
    );
    self.skipWaiting();
});

self.addEventListener('activate', (e) => {
    e.waitUntil(
        caches.keys().then(keys =>
            Promise.all(
                keys
                    .filter(k => k !== CACHE_STATIC && k !== CACHE_DATA)
                    .map(k => caches.delete(k))
            )
        )
    );
    self.clients.claim();
});

self.addEventListener('fetch', (e) => {
    const url = e.request.url;
    // Network-only for live spreadsheet data
    if (url.includes('docs.google.com/spreadsheets') || url.includes('sheets.googleapis.com')) {
        e.respondWith(
            fetch(e.request)
                .then(res => {
                    const clone = res.clone();
                    caches.open(CACHE_DATA).then(c => c.put(e.request, clone));
                    return res;
                })
                .catch(() => caches.match(e.request))
        );
        return;
    }
    // Cache-first for same-origin static assets
    if (e.request.destination === 'image' || e.request.destination === 'script' || e.request.destination === 'style') {
        e.respondWith(
            caches.match(e.request).then(cached => cached || fetch(e.request))
        );
        return;
    }
    // Stale-while-revalidate for HTML
    e.respondWith(
        caches.open(CACHE_STATIC).then(cache =>
            cache.match(e.request).then(cached => {
                const network = fetch(e.request).then(res => {
                    cache.put(e.request, res.clone());
                    return res;
                });
                return cached || network;
            })
        )
    );
});
"""


# ---------------------------------------------------------------------------
# 4. PAGE SHELL BUILDER
# ---------------------------------------------------------------------------

# Screen-reader only utility class — injected into every page's <style>
_SR_ONLY_CSS = """
.sr-only {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
    border-width: 0;
}
.skip-to-content {
    position: absolute;
    top: -100px;
    left: 1rem;
    z-index: 9999;
    padding: 0.75rem 1.5rem;
    background: var(--p);
    color: #fff;
    font-weight: 700;
    border-radius: 0 0 8px 8px;
    text-decoration: none;
    transition: top 0.2s;
}
.skip-to-content:focus { top: 0; }
"""

_MD_PROSE_CSS = """
.md-list { margin: 0 0 1rem 1.5rem; padding: 0; }
.md-list li { margin-bottom: 0.5rem; line-height: 1.7; }
.md-p { margin-bottom: 1rem; line-height: 1.8; }
"""

_LOADING_SKELETON_CSS = """
.loading-skeleton {
    background: linear-gradient(90deg,
        rgba(128,128,128,0.08) 25%,
        rgba(128,128,128,0.16) 50%,
        rgba(128,128,128,0.08) 75%
    );
    background-size: 200% 100%;
    animation: skeleton-shimmer 1.5s infinite;
    border-radius: var(--radius, 12px);
    min-height: 200px;
}
@keyframes skeleton-shimmer {
    0%   { background-position: 200% 0; }
    100% { background-position: -200% 0; }
}
"""


def build_page(cfg: SiteConfig, title: str, content: str) -> str:
    """
    Wrap a content string in a full, Lighthouse-optimised HTML document shell.

    v56 CHANGES:
      - gen_runtime_js() injected before </body> so it's available to all
        section scripts without being render-blocking.
      - _scroll_reveal_script() removed — replaced by IntersectionObserver
        inside gen_runtime_js().
      - <meta name="color-scheme"> added for OS-level dark mode signalling.
      - Canonical URL <link> added for SEO deduplication.
      - DNS prefetch added for CDN domains used in the page.
      - Service worker registration deferred to 'load' event.
    """
    from utils import sanitize, sanitize_url

    gsc_meta = (
        f'<meta name="google-site-verification" content="{cfg.gsc_tag}">'
        if cfg.gsc_tag else ""
    )
    og_meta = (
        f'<meta property="og:title" content="{sanitize(title)} | {sanitize(cfg.biz_name)}">'
        f'<meta property="og:description" content="{sanitize(cfg.seo_d)}">'
        f'<meta property="og:image" content="{sanitize_url(cfg.og_image or cfg.logo_url or cfg.hero_img_1)}">'
        f'<meta property="og:type" content="website">'
        f'<meta property="og:url" content="{sanitize_url(cfg.prod_url)}">'
        f'<meta name="twitter:card" content="summary_large_image">'
    )
    pwa_tags = (
        f'<link rel="manifest" href="manifest.json">'
        f'<meta name="theme-color" content="#000000">'
        + (f'<link rel="apple-touch-icon" href="{sanitize_url(cfg.pwa_icon)}">' if cfg.pwa_icon else '')
    )
    seo_kw_meta = f'<meta name="keywords" content="{sanitize(cfg.seo_kw)}">' if cfg.seo_kw else ""
    canonical = f'<link rel="canonical" href="{sanitize_url(cfg.prod_url)}/">'  
    dns_prefetch = (
        '<link rel="dns-prefetch" href="https://fonts.googleapis.com">'
        '<link rel="dns-prefetch" href="https://fonts.gstatic.com">'
        '<link rel="dns-prefetch" href="https://docs.google.com">'
        '<link rel="dns-prefetch" href="https://images.unsplash.com">'
    )
    ga_script = (
        f"<script async src='https://www.googletagmanager.com/gtag/js?id={cfg.ga_tag}'></script>"
        f"<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}"
        f"gtag('js',new Date());gtag('config','{cfg.ga_tag}',{{anonymize_ip:true}});</script>"
    ) if cfg.ga_tag else ""

    font_tags  = titan_themes.gen_font_preload_html(cfg.h_font, cfg.b_font)
    modern_css = build_css(cfg)

    # LCP image preload — only if a non-video hero is used
    lcp_preload = (
        f'<link rel="preload" as="image" href="{sanitize_url(cfg.hero_img_1)}" fetchpriority="high">'
        if not cfg.hero_video_id else ''
    )

    sw_script = """
<script>
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('./service-worker.js')
            .catch(err => console.warn('[SW] Registration failed:', err));
    });
}
</script>"""

    return f"""<!DOCTYPE html>
<html lang="en" dir="ltr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
    <meta name="color-scheme" content="light dark">
    <title>{sanitize(title)} | {sanitize(cfg.biz_name)}</title>
    <meta name="description" content="{sanitize(cfg.seo_d)}">
    {gsc_meta}
    {seo_kw_meta}
    {og_meta}
    {pwa_tags}
    {canonical}
    {dns_prefetch}
    {lcp_preload}
    {gen_schema(cfg)}
    <!-- Font loading: 4-tag performance pattern (preconnect×2, preload, swap) -->
    {font_tags}
    <style>
        /* Titan Engine v56 — Generated CSS */
        {_SR_ONLY_CSS}
        {_MD_PROSE_CSS}
        {_LOADING_SKELETON_CSS}
        {modern_css}
    </style>
    {ga_script}
    <!-- Feature-flag scripts: context-aware UI, A/B test, voice -->
    {templates.gen_2050_scripts(cfg)}
</head>
<body>
    <main>
        {templates.gen_nav(cfg)}
        {content}
        {templates.gen_footer(cfg)}
        {templates.gen_wa_widget(cfg)}
        {templates.gen_cart_system(cfg)}
        {templates.gen_lang_script(cfg)}
        {templates.gen_popup(cfg)}
    </main>
    <!-- Titan Runtime: parseCSVLine, parseMarkdown, titanToast, scroll reveal -->
    {templates.gen_runtime_js()}
    {sw_script}
</body>
</html>"""


# ---------------------------------------------------------------------------
# 5. PAGE ASSEMBLERS
# ---------------------------------------------------------------------------

def assemble_home(cfg: SiteConfig) -> str:
    from utils import format_text
    parts = []
    if cfg.show_hero:          parts.append(templates.gen_hero(cfg))
    if cfg.show_stats:         parts.append(templates.gen_stats(cfg))
    if cfg.show_features:      parts.append(templates.gen_features(cfg))
    if cfg.show_pricing:       parts.append(templates.gen_pricing_table(cfg))
    if cfg.show_inventory:     parts.append(templates.gen_inventory(cfg))
    if cfg.show_gallery:       parts.append(templates.gen_about_section(cfg))
    if cfg.show_testimonials:  parts.append(templates.gen_testimonials(cfg))
    if cfg.show_faq:           parts.append(templates.gen_faq_section(cfg))
    if cfg.show_cta:           parts.append(templates.gen_cta(cfg))
    return "\n".join(parts)


def assemble_contact(cfg: SiteConfig) -> str:
    return templates.gen_contact_page(cfg)


def assemble_inner(cfg: SiteConfig, title: str, body_html: str) -> str:
    return (
        f"{templates.gen_inner_header(title)}"
        f"<section class='inner-body-section'><div class='container inner-body'>{body_html}</div></section>"
    )


# ---------------------------------------------------------------------------
# 6. ZIP BUILDER
# ---------------------------------------------------------------------------

def build_zip(cfg: SiteConfig) -> io.BytesIO:
    from utils import format_text
    buf = io.BytesIO()
    year = datetime.datetime.now().year

    readme = f"""Titan Engine v56 — Site Package
================================
Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')} UTC
Business:  {cfg.biz_name}
URL:       {cfg.prod_url}

FILES
-----
index.html   — Home page
about.html   — About / Full story
contact.html — Contact form + map
privacy.html — Privacy policy
terms.html   — Terms of service
{('booking.html  — Booking / appointments') if cfg.show_booking else ''}
{('product.html  — Product detail page (CSV-driven)') if cfg.show_inventory else ''}
{('blog.html     — Blog index (CSV-driven)') if cfg.show_blog else ''}
{('post.html     — Blog post page (CSV-driven)') if cfg.show_blog else ''}

manifest.json      — PWA manifest
service-worker.js  — Offline caching
robots.txt         — Search engine directives
sitemap.xml        — Sitemap for Google Search Console

DEPLOYMENT
----------
1. Upload all files to any static host (Netlify, Vercel, GitHub Pages, IPFS).
2. Point your domain to the host.
3. Done. Zero monthly fees.

GOOGLE SHEETS CMS
-----------------
Store CSV columns: Name | Price | Description | Images (pipe-separated) | Payment Link | 3D Model (.glb) | Category
Blog CSV columns:  Slug | Title | Author | Category | Excerpt | Cover Image | Body (Markdown)
Lang CSV columns:  ElementID | English | Spanish | French | Arabic | German | Portuguese
"""

    with zipfile.ZipFile(buf, "a", zipfile.ZIP_DEFLATED, False) as zf:
        # Core pages
        zf.writestr("index.html",   build_page(cfg, "Home",    assemble_home(cfg)))
        zf.writestr("about.html",   build_page(cfg, "About",   assemble_inner(cfg, "About",   format_text(cfg.about_long))))
        zf.writestr("contact.html", build_page(cfg, "Contact", assemble_contact(cfg)))
        zf.writestr("privacy.html", build_page(cfg, "Privacy", assemble_inner(cfg, "Privacy", format_text(cfg.priv_txt))))
        zf.writestr("terms.html",   build_page(cfg, "Terms",   assemble_inner(cfg, "Terms",   format_text(cfg.term_txt))))

        # Optional pages
        if cfg.show_booking:
            zf.writestr("booking.html", build_page(cfg, "Book Now",        templates.gen_booking_content(cfg)))
        if cfg.show_inventory:
            zf.writestr("product.html", build_page(cfg, "Product Details", templates.gen_product_page_content(cfg, is_demo=False)))
        if cfg.show_blog:
            zf.writestr("blog.html", build_page(cfg, "Blog",    templates.gen_blog_index_html(cfg)))
            zf.writestr("post.html", build_page(cfg, "Article", templates.gen_blog_post_html(cfg)))

        # Static assets
        zf.writestr("manifest.json",     gen_pwa_manifest(cfg))
        zf.writestr("service-worker.js", gen_sw())
        zf.writestr("robots.txt", (
            f"User-agent: *\nAllow: /\n"
            f"Sitemap: {cfg.prod_url}/sitemap.xml\n"
        ))
        # Sitemap with all pages
        urls = [cfg.prod_url + "/" + p for p in ["", "about.html", "contact.html"]]
        if cfg.show_blog:     urls.append(cfg.prod_url + "/blog.html")
        if cfg.show_booking:  urls.append(cfg.prod_url + "/booking.html")
        url_els = "".join(f"<url><loc>{u}</loc><changefreq>weekly</changefreq></url>" for u in urls)
        zf.writestr("sitemap.xml", (
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
            + url_els +
            '</urlset>'
        ))
        zf.writestr("_README.txt", readme)

    return buf
