# compiler.py
# The HTML compilation layer. Zero Streamlit imports.
#
# Responsibilities:
#   - SiteConfig: typed dataclass that holds every user input collected by app.py
#   - build_page(): wraps a content string in the full HTML shell
#   - assemble_*(): orchestrate section order for each page
#   - build_zip(): produce the final downloadable package as a BytesIO object
#
# Dependency chain:  compiler.py  →  templates.py  →  utils.py
#                    compiler.py  →  titan_themes.py

from __future__ import annotations

import io
import json
import zipfile
import datetime
from dataclasses import dataclass, field

import titan_themes
import templates


# ---------------------------------------------------------------------------
# 1. SITE CONFIG DATACLASS
# ---------------------------------------------------------------------------
# Every field maps 1-to-1 to a widget in app.py.
# Using a dataclass means:
#   - All fields have type hints — easier to refactor and grep.
#   - app.py does ONE cfg = SiteConfig(...) call, then passes cfg everywhere.
#   - Template functions never read Streamlit globals — they accept cfg as an arg.


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
    show_hero:        bool = True
    show_stats:       bool = True
    show_features:    bool = True
    show_pricing:     bool = True
    show_inventory:   bool = True
    show_blog:        bool = True
    show_gallery:     bool = True
    show_testimonials: bool = True
    show_faq:         bool = True
    show_cta:         bool = True
    show_booking:     bool = True

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
# 2. CSS BUILDER  (thin wrapper around titan_themes)
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
    schema = {
        "@context": "https://schema.org",
        "@type": "LocalBusiness",
        "name": cfg.biz_name,
        "image": cfg.logo_url or cfg.hero_img_1,
        "telephone": cfg.biz_phone,
        "email": cfg.biz_email,
        "url": cfg.prod_url,
        "description": cfg.seo_d,
    }
    return f'<script type="application/ld+json">{json.dumps(schema)}</script>'


def gen_pwa_manifest(cfg: SiteConfig) -> str:
    theme = titan_themes.THEME_REGISTRY.get(
        cfg.theme_mode,
        titan_themes.THEME_REGISTRY["1. Stripe Cloud (Modern SaaS)"]
    )
    return json.dumps({
        "name": cfg.biz_name,
        "short_name": cfg.pwa_short,
        "start_url": "./index.html",
        "display": "standalone",
        "background_color": theme['bg'],
        "theme_color": theme['p'],
        "description": cfg.pwa_desc,
        "icons": [{"src": cfg.pwa_icon, "sizes": "512x512", "type": "image/png", "purpose": "any maskable"}],
    })


def gen_sw() -> str:
    """Service worker — no user data injected, so no cfg arg needed."""
    return """
const CACHE_NAME = 'titan-v55-cache';
const urlsToCache = ['./index.html','./about.html','./contact.html','./product.html','./blog.html','./post.html'];

self.addEventListener('install', (e) => {
    e.waitUntil(caches.open(CACHE_NAME).then((cache) => cache.addAll(urlsToCache)));
    self.skipWaiting();
});

self.addEventListener('fetch', (e) => {
    if (e.request.url.includes('google.com/spreadsheets')) {
        e.respondWith(fetch(e.request).then(res => {
            const resClone = res.clone();
            caches.open('titan-data').then(cache => cache.put(e.request, resClone));
            return res;
        }).catch(() => caches.match(e.request)));
    } else {
        e.respondWith(caches.match(e.request).then((response) => response || fetch(e.request)));
    }
});
"""


# ---------------------------------------------------------------------------
# 4. PAGE SHELL BUILDER
# ---------------------------------------------------------------------------

def build_page(cfg: SiteConfig, title: str, content: str) -> str:
    """
    Wrap a content string in a full HTML document shell.
    This is the only place that touches <html>/<head>/<body>.
    """
    gsc_meta   = f'<meta name="google-site-verification" content="{cfg.gsc_tag}">' if cfg.gsc_tag else ""
    og_meta    = (
        f'<meta property="og:title" content="{title} | {cfg.biz_name}">'
        f'<meta property="og:description" content="{cfg.seo_d}">'
        f'<meta property="og:image" content="{cfg.og_image or cfg.logo_url}">'
        f'<meta name="twitter:card" content="summary_large_image">'
    )
    pwa_tags   = (
        f'<link rel="manifest" href="manifest.json">'
        f'<meta name="theme-color" content="#000000">'
        f'<link rel="apple-touch-icon" href="{cfg.pwa_icon}">'
    )
    sw_script  = "<script>if('serviceWorker' in navigator){navigator.serviceWorker.register('service-worker.js');}</script>"
    ga_script  = (
        f"<script async src='https://www.googletagmanager.com/gtag/js?id={cfg.ga_tag}'></script>"
        f"<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','{cfg.ga_tag}');</script>"
    ) if cfg.ga_tag else ""

    # Font loading — delegate entirely to titan_themes so the preload URL,
    # weight set, and @font-face size-adjust block stay in perfect sync.
    font_tags  = titan_themes.gen_font_preload_html(cfg.h_font, cfg.b_font)
    modern_css = build_css(cfg)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | {cfg.biz_name}</title>
    <meta name="description" content="{cfg.seo_d}">
    {gsc_meta}{og_meta}{pwa_tags}{gen_schema(cfg)}
    <!-- LCP image preload — fetchpriority tells the browser this is the most
         important resource on the page, eliminating the LCP discovery delay -->
    <link rel="preload" as="image" href="{cfg.hero_img_1}" fetchpriority="high">
    <!-- Font loading — 4-tag performance pattern (preconnect×2, preload, swap) -->
    {font_tags}
    <style>{modern_css}</style>
    {ga_script}
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
    {_scroll_reveal_script()}
    {sw_script}
</body>
</html>"""


def _scroll_reveal_script() -> str:
    return (
        "<script defer>window.addEventListener('scroll',()=>{"
        "var r=document.querySelectorAll('.reveal');"
        "for(var i=0;i<r.length;i++){"
        "if(r[i].getBoundingClientRect().top<window.innerHeight-100)"
        "r[i].classList.add('active');}});"
        "window.dispatchEvent(new Event('scroll'));</script>"
    )


# ---------------------------------------------------------------------------
# 5. PAGE ASSEMBLERS
# ---------------------------------------------------------------------------
# Each assembler builds the <main> content for one page type.
# They call templates.gen_*() for sections, then return the joined string.
# build_page() wraps the result in the HTML shell.

def assemble_home(cfg: SiteConfig) -> str:
    from utils import format_text
    parts = []
    if cfg.show_hero:        parts.append(templates.gen_hero(cfg))
    if cfg.show_stats:       parts.append(templates.gen_stats(cfg))
    if cfg.show_features:    parts.append(templates.gen_features(cfg))
    if cfg.show_pricing:     parts.append(templates.gen_pricing_table(cfg))
    if cfg.show_inventory:   parts.append(templates.gen_inventory(cfg))
    if cfg.show_gallery:     parts.append(templates.gen_about_section(cfg))
    if cfg.show_testimonials: parts.append(templates.gen_testimonials(cfg))
    if cfg.show_faq:         parts.append(templates.gen_faq_section(cfg))
    if cfg.show_cta:         parts.append(templates.gen_cta(cfg))
    return "\n".join(parts)


def assemble_contact(cfg: SiteConfig) -> str:
    return templates.gen_contact_page(cfg)


def assemble_inner(cfg: SiteConfig, title: str, body_html: str) -> str:
    return f"{templates.gen_inner_header(title)}<section><div class='container'>{body_html}</div></section>"


# ---------------------------------------------------------------------------
# 6. ZIP BUILDER
# ---------------------------------------------------------------------------

def build_zip(cfg: SiteConfig) -> io.BytesIO:
    """Build the complete downloadable site package and return it as BytesIO."""
    from utils import format_text

    buf = io.BytesIO()
    year = datetime.datetime.now().year

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
        zf.writestr("manifest.json",      gen_pwa_manifest(cfg))
        zf.writestr("service-worker.js",  gen_sw())
        zf.writestr("robots.txt",         f"User-agent: *\nAllow: /\nSitemap: {cfg.prod_url}/sitemap.xml")
        zf.writestr("sitemap.xml", (
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
            f'<url><loc>{cfg.prod_url}/</loc></url>'
            '</urlset>'
        ))

    return buf
