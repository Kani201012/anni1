# app.py  (v55 — Refactored)
# ─────────────────────────────────────────────────────────────────
# This file is ONLY responsible for:
#   1. Streamlit UI (sidebar, tabs, widgets)
#   2. Packing widget values into a SiteConfig dataclass
#   3. Calling compiler.build_page() and rendering the result
#   4. Building the ZIP and handling download / IPFS push
#
# It NEVER builds an HTML string itself.
# All HTML generation lives in templates.py, orchestrated by compiler.py.
# ─────────────────────────────────────────────────────────────────

import streamlit as st
import io
import json
import requests

import titan_themes
from compiler import SiteConfig, build_page, build_zip, assemble_home, assemble_contact, assemble_inner
import templates
from utils import format_text

# ─────────────────────────────────────────────────────────────────
# 0. SESSION STATE DEFAULTS
# ─────────────────────────────────────────────────────────────────

def _init(key, val):
    if key not in st.session_state:
        st.session_state[key] = val

_init('hero_h',    "Stop Paying Rent for Your Website.")
_init('hero_sub',  "The Titan Engine. Pay once. Own it forever.")
_init('about_h',   "Control Your Empire from a Spreadsheet")
_init('about_short', "No plugins. No dashboard. Just a Google Sheet.")
_init('feat_data', (
    "bolt | The Performance Pillar | **0.1s High-Velocity Loading**. Titan loads instantly.\n"
    "wallet | The Economic Pillar | **$0 Monthly Fees**. Hosting subscriptions eliminated.\n"
    "table | The Functional Pillar | **Google Sheets CMS**. Update from a spreadsheet.\n"
    "shield | The Authority Pillar | **Unhackable Security**. Zero-DB Architecture.\n"
    "layers | The Reliability Pillar | **Global Edge Deployment**. 100+ servers.\n"
    "star | The Conversion Pillar | **One-Tap WhatsApp**. Direct-to-Chat technology."
))

# ─────────────────────────────────────────────────────────────────
# 1. PAGE CONFIG
# ─────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Titan Architect | v55 Apex",
    layout="wide",
    page_icon="⚡",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
:root{--primary:#0f172a;--accent:#ef4444}
.stApp{background-color:#f8fafc;color:#1e293b;font-family:'Inter',sans-serif}
[data-testid="stSidebar"]{background-color:#ffffff;border-right:1px solid #e2e8f0}
[data-testid="stSidebar"] h1{
    background:linear-gradient(90deg,#0f172a,#ef4444);
    -webkit-background-clip:text;-webkit-text-fill-color:transparent;
    font-weight:900!important;font-size:1.8rem!important
}
.stTextInput input,.stTextArea textarea{
    background-color:#ffffff!important;border:1px solid #cbd5e1!important;
    border-radius:8px!important;color:#0f172a!important
}
.stButton>button{
    width:100%;border-radius:8px;height:3.5rem;
    background:linear-gradient(135deg,#0f172a 0%,#334155 100%);
    color:white;font-weight:800;border:none;
    box-shadow:0 4px 15px rgba(15,23,42,0.3);
    text-transform:uppercase;letter-spacing:1px;transition:transform 0.2s
}
.stButton>button:hover{transform:translateY(-2px)}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
# 2. SIDEBAR
# ─────────────────────────────────────────────────────────────────

with st.sidebar:
    st.title("Titan Architect")
    st.caption("v55.0 | Edge-Dynamic Architecture")
    st.divider()

    # ── AI GENERATOR ──────────────────────────────────────────────
    with st.expander("🤖 AI Copy Generator", expanded=False):
        raw_key  = st.text_input("Groq API Key", type="password")
        biz_desc = st.text_input("Business Description")
        if st.button("✨ Generate Copy"):
            if not raw_key.strip() or not biz_desc:
                st.error("API key and description required.")
            else:
                try:
                    with st.spinner("Writing…"):
                        url  = "https://api.groq.com/openai/v1/chat/completions"
                        hdrs = {"Authorization": f"Bearer {raw_key.strip()}", "Content-Type": "application/json"}
                        prompt = (
                            f"Act as a copywriter. Return JSON for '{biz_desc}': "
                            "hero_h, hero_sub, about_h, about_short, feat_data (icon|Title|Desc format)."
                        )
                        data = {
                            "messages": [{"role": "user", "content": prompt}],
                            "model": "llama-3.1-8b-instant",
                            "response_format": {"type": "json_object"},
                        }
                        resp = requests.post(url, headers=hdrs, json=data)
                        if resp.status_code == 200:
                            parsed = json.loads(resp.json()['choices'][0]['message']['content'])
                            for key in ('hero_h', 'hero_sub', 'about_h', 'about_short'):
                                if key in parsed:
                                    st.session_state[key] = str(parsed[key])
                            if 'feat_data' in parsed:
                                fd = parsed['feat_data']
                                st.session_state.feat_data = "\n".join(map(str, fd)) if isinstance(fd, list) else str(fd)
                            st.success("Generated!")
                            st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

    # ── DESIGN STUDIO + TYPOGRAPHY (merged — was two expanders) ───
    with st.expander("🎨 Design Studio", expanded=True):
        theme_names = list(titan_themes.THEME_REGISTRY.keys())
        theme_mode  = st.selectbox("Theme", theme_names)
        st.divider()
        c1, c2 = st.columns(2)
        hero_layout = c1.selectbox("Hero Alignment", ["Center", "Left"])
        h_font      = c1.selectbox("Heading Font",   ["Space Grotesk", "Montserrat", "Playfair Display", "Outfit"])
        b_font      = c2.selectbox("Body Font",       ["Inter", "Plus Jakarta Sans", "Roboto"])
        col_h       = c2.color_picker("Heading Color",   "#0f172a")
        col_b       = c2.color_picker("Body Color",      "#475569")
        st.divider()
        size_h1     = st.slider("H1 Size (rem)", 1.0, 8.0, 4.5)
        size_p      = st.slider("Body Size (rem)", 0.8, 2.0, 1.1)
        st.divider()
        cta_bg      = st.color_picker("CTA Background", "#10b981")
        cta_txt     = st.color_picker("CTA Text",       "#ffffff")

    # ── FEATURES + SECTIONS (merged — was two expanders) ──────────
    with st.expander("🚀 Features & Sections", expanded=True):
        st.markdown("**Capability flags**")
        enable_ar      = st.checkbox("AR 3D Models",        value=True)
        enable_voice   = st.checkbox("Voice Search",        value=True)
        enable_context = st.checkbox("Context-Aware UI",    value=True)
        enable_ab      = st.checkbox("A/B Testing",         value=True)
        st.divider()
        st.markdown("**Page sections**")
        sc1, sc2 = st.columns(2)
        show_hero        = sc1.checkbox("Hero",          value=True)
        show_stats       = sc1.checkbox("Stats",         value=True)
        show_features    = sc1.checkbox("Features",      value=True)
        show_pricing     = sc1.checkbox("Pricing",       value=True)
        show_inventory   = sc1.checkbox("Store",         value=True)
        show_blog        = sc1.checkbox("Blog",          value=True)
        show_gallery     = sc2.checkbox("About",         value=True)
        show_testimonials= sc2.checkbox("Testimonials",  value=True)
        show_faq         = sc2.checkbox("FAQ",           value=True)
        show_cta         = sc2.checkbox("Final CTA",     value=True)
        show_booking     = sc2.checkbox("Booking",       value=True)

    # ── SEO & ANALYTICS + IPFS (merged) ───────────────────────────
    with st.expander("⚙️ SEO, Analytics & Deploy", expanded=False):
        seo_area   = st.text_input("Service Area", "Global / Online")
        gsc_tag    = st.text_input("Google Verification ID")
        ga_tag     = st.text_input("Google Analytics ID")
        og_image   = st.text_input("Social Share Image URL")
        st.divider()
        pinata_jwt = st.text_input("Pinata JWT (IPFS deploy)", type="password",
                                   help="Leave blank for ZIP download.")


# ─────────────────────────────────────────────────────────────────
# 3. MAIN WORKSPACE TABS
# ─────────────────────────────────────────────────────────────────

st.title("🏗️ Titan Engine v55 Compiler")

tab_labels = ["1. Identity", "2. Content", "3. Marketing", "4. Pricing", "5. Store", "6. Booking", "7. Blog", "8. Legal"]
tabs = st.tabs(tab_labels)

# TAB 1 — IDENTITY
with tabs[0]:
    c1, c2 = st.columns(2)
    biz_name    = c1.text_input("Business Name",    "StopWebRent.com")
    biz_tagline = c1.text_input("Tagline",          "Stop Renting. Start Owning.")
    biz_phone   = c1.text_input("Phone",            "966572562151")
    biz_email   = c1.text_input("Email",            "hello@example.com")
    prod_url    = c2.text_input("Website URL",      "https://www.stopwebrent.com")
    biz_addr    = c2.text_area ("Address",          "Kaydiem Script Lab\nKolkata, India", height=80)
    map_iframe  = c2.text_area ("Google Map Embed", placeholder='<iframe src="..."></iframe>', height=80)
    seo_d       = c2.text_area ("Meta Description", "Stop paying monthly fees.", height=80)
    logo_url    = c2.text_input("Logo URL")

    st.subheader("📱 PWA")
    p1, p2, p3 = st.columns(3)
    pwa_short = p1.text_input("App Short Name",   biz_name[:12])
    pwa_desc  = p2.text_input("App Description",  "Official App")
    pwa_icon  = p3.text_input("App Icon (512px)", logo_url)

    st.subheader("🌍 Multi-Language CSV")
    lang_sheet = st.text_input("Translation Sheet URL")

    st.subheader("Social Links")
    s1, s2, s3 = st.columns(3)
    fb_link = s1.text_input("Facebook")
    ig_link = s2.text_input("Instagram")
    x_link  = s3.text_input("X (Twitter)")
    s4, s5, s6 = st.columns(3)
    li_link = s4.text_input("LinkedIn")
    yt_link = s5.text_input("YouTube")
    wa_num  = s6.text_input("WhatsApp Number", "966572562151")

# TAB 2 — CONTENT
with tabs[1]:
    st.subheader("Hero")
    hero_h        = st.text_input("Headline",           key="hero_h")
    hero_sub      = st.text_input("Subtext",            key="hero_sub")
    hero_badge_txt= st.text_input("Badge Text",         "🚀 Next-Generation Architecture")
    hero_video_id = st.text_input("YouTube BG Override", placeholder="e.g. dQw4w9WgXcQ")
    hc1, hc2, hc3 = st.columns(3)
    hero_img_1 = hc1.text_input("Slide 1", "https://images.unsplash.com/photo-1460925895917-afdab827c52f?q=80&w=1600")
    hero_img_2 = hc2.text_input("Slide 2", "https://images.unsplash.com/photo-1551288049-bebda4e38f71?q=80&w=1600")
    hero_img_3 = hc3.text_input("Slide 3", "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?q=80&w=1600")

    st.divider()
    st.subheader("Stats")
    cs1, cs2, cs3 = st.columns(3)
    stat_1  = cs1.text_input("Stat 1", "0.1s");  label_1 = cs1.text_input("Label 1", "Speed")
    stat_2  = cs2.text_input("Stat 2", "$0");    label_2 = cs2.text_input("Label 2", "Fees")
    stat_3  = cs3.text_input("Stat 3", "100%");  label_3 = cs3.text_input("Label 3", "Ownership")

    st.divider()
    st.subheader("Features")
    f_title        = st.text_input("Section Title", "Value Pillars")
    feat_data_input = st.text_area("Features (icon|Title|Desc per line)", key="feat_data", height=150)

    st.divider()
    st.subheader("About")
    about_h_in    = st.text_input("About Title",    key="about_h")
    about_img     = st.text_input("About Image",    "https://images.unsplash.com/photo-1543286386-713df548e9cc?q=80&w=1600")
    about_short_in= st.text_area("Short Summary",   key="about_short", height=80)
    about_long    = st.text_area("Full About Page", "The Digital Landlord Trap…", height=180)

# TAB 3 — MARKETING
with tabs[2]:
    top_bar_enabled = st.checkbox("Enable Top Bar")
    top_bar_text    = st.text_input("Promo Text",  "🔥 50% OFF Launch Sale - Ends Soon!")
    top_bar_link    = st.text_input("Promo Link",  "#pricing")
    st.divider()
    popup_enabled   = st.checkbox("Enable Popup")
    popup_delay     = st.slider("Popup Delay (s)", 1, 30, 5)
    popup_title     = st.text_input("Popup Headline", "Wait! Don't leave empty handed.")
    popup_text      = st.text_input("Popup Body",     "Get our free pricing guide on WhatsApp.")
    popup_cta       = st.text_input("Popup Button",   "Get it Now")

# TAB 4 — PRICING
with tabs[3]:
    cp1, cp2, cp3 = st.columns(3)
    titan_price = cp1.text_input("Setup Price", "$199")
    titan_mo    = cp1.text_input("Monthly Fee", "$0")
    wix_name    = cp2.text_input("Competitor",  "Wix")
    wix_mo      = cp2.text_input("Comp. Monthly","$29/mo")
    save_val    = cp3.text_input("Savings",     "$1,466")

# TAB 5 — STORE
with tabs[4]:
    st.info("💡 Column F of your CSV can hold a `.glb` URL to enable AR 3D viewing.")
    sheet_url   = st.text_input("Store CSV URL")
    custom_feat = st.text_input("Default Product Image", "https://images.unsplash.com/photo-1460925895917-afdab827c52f?q=80&w=800")
    cpy1, cpy2  = st.columns(2)
    paypal_link = cpy1.text_input("PayPal Link",  "https://paypal.me/yourid")
    upi_id      = cpy2.text_input("UPI ID",       "name@upi")

# TAB 6 — BOOKING
with tabs[5]:
    booking_title = st.text_input("Section Title",  "Book an Appointment")
    booking_desc  = st.text_input("Subtext",        "Select a time slot.")
    booking_embed = st.text_area("Embed Code", height=150, value=(
        '<!-- Calendly -->\n'
        '<div class="calendly-inline-widget" data-url="https://calendly.com/demo/30min" style="min-width:320px;height:630px;"></div>\n'
        '<script src="https://assets.calendly.com/assets/external/widget.js" async></script>'
    ))

# TAB 7 — BLOG
with tabs[6]:
    blog_sheet_url  = st.text_input("Blog CSV URL")
    blog_hero_title = st.text_input("Blog Section Title", "Latest Insights")
    blog_hero_sub   = st.text_input("Blog Subtext",       "Thoughts on tech.")

# TAB 8 — LEGAL / CONTENT
with tabs[7]:
    testi_data = st.text_area("Testimonials (Name | Quote, one per line)", height=100,
                              value="Rajesh Gupta | Titan stopped the bleeding.\nSarah Jenkins | Easy updates.")
    faq_data   = st.text_area("FAQ (Question ? Answer, one per line)", height=100,
                              value="Do I pay $0 monthly ? Yes, hosting is free.\nIs it secure ? Yes, zero-DB architecture.")
    priv_txt   = st.text_area("Privacy Policy",    "We collect minimum data.", height=80)
    term_txt   = st.text_area("Terms of Service",  "You own the code.",        height=80)


# ─────────────────────────────────────────────────────────────────
# 4. PACK ALL WIDGET VALUES INTO SiteConfig
# ─────────────────────────────────────────────────────────────────
# This is the ONLY place in app.py that touches SiteConfig fields.
# Every generator function below receives `cfg` — never raw widget vars.

cfg = SiteConfig(
    # Identity
    biz_name=biz_name, biz_tagline=biz_tagline, biz_phone=biz_phone, biz_email=biz_email,
    biz_addr=biz_addr, prod_url=prod_url, logo_url=logo_url, map_iframe=map_iframe, seo_d=seo_d,
    # PWA
    pwa_short=pwa_short, pwa_desc=pwa_desc, pwa_icon=pwa_icon,
    # Social
    fb_link=fb_link, ig_link=ig_link, x_link=x_link, li_link=li_link, yt_link=yt_link, wa_num=wa_num,
    # Theme
    theme_mode=theme_mode, hero_layout=hero_layout, h_font=h_font, b_font=b_font,
    col_h=col_h, col_b=col_b, size_h1=size_h1, size_p=size_p,
    cta_bg_color=cta_bg, cta_txt_color=cta_txt,
    # Features
    enable_ar=enable_ar, enable_voice=enable_voice, enable_context=enable_context, enable_ab=enable_ab,
    # Sections
    show_hero=show_hero, show_stats=show_stats, show_features=show_features, show_pricing=show_pricing,
    show_inventory=show_inventory, show_blog=show_blog, show_gallery=show_gallery,
    show_testimonials=show_testimonials, show_faq=show_faq, show_cta=show_cta, show_booking=show_booking,
    # SEO
    seo_area=seo_area, gsc_tag=gsc_tag, ga_tag=ga_tag, og_image=og_image,
    # Hero
    hero_h=hero_h, hero_sub=hero_sub, hero_badge_txt=hero_badge_txt, hero_video_id=hero_video_id,
    hero_img_1=hero_img_1, hero_img_2=hero_img_2, hero_img_3=hero_img_3,
    # Stats
    stat_1=stat_1, label_1=label_1, stat_2=stat_2, label_2=label_2, stat_3=stat_3, label_3=label_3,
    # Features
    f_title=f_title, feat_data=feat_data_input,
    # About
    about_h=about_h_in, about_img=about_img, about_short=about_short_in, about_long=about_long,
    # Marketing
    top_bar_enabled=top_bar_enabled, top_bar_text=top_bar_text, top_bar_link=top_bar_link,
    popup_enabled=popup_enabled, popup_delay=popup_delay, popup_title=popup_title,
    popup_text=popup_text, popup_cta=popup_cta,
    # Pricing
    titan_price=titan_price, titan_mo=titan_mo, wix_name=wix_name, wix_mo=wix_mo, save_val=save_val,
    # Store
    sheet_url=sheet_url, custom_feat=custom_feat, paypal_link=paypal_link, upi_id=upi_id,
    # Booking
    booking_embed=booking_embed, booking_title=booking_title, booking_desc=booking_desc,
    # Blog
    blog_sheet_url=blog_sheet_url, blog_hero_title=blog_hero_title, blog_hero_sub=blog_hero_sub,
    # Content
    testi_data=testi_data, faq_data=faq_data, priv_txt=priv_txt, term_txt=term_txt,
    lang_sheet=lang_sheet, pinata_jwt=pinata_jwt,
)


# ─────────────────────────────────────────────────────────────────
# 5. PREVIEW & DEPLOY
# ─────────────────────────────────────────────────────────────────

st.divider()
st.subheader("🚀 Launchpad")

nav1, nav2 = st.columns([3, 1])
preview_mode = nav1.radio(
    "Preview Page:",
    ["Home", "About", "Contact", "Blog Index", "Blog Post", "Privacy", "Terms", "Product (Demo)", "Booking"],
    horizontal=True,
)
device_mode = nav2.radio("View:", ["💻 Desktop", "📱 Mobile"], horizontal=True)

# Build the correct page based on preview selection
match preview_mode:
    case "Home":
        html_to_render = build_page(cfg, "Home",    assemble_home(cfg))
    case "About":
        html_to_render = build_page(cfg, "About",   assemble_inner(cfg, "About",   format_text(cfg.about_long)))
    case "Contact":
        html_to_render = build_page(cfg, "Contact", assemble_contact(cfg))
    case "Privacy":
        html_to_render = build_page(cfg, "Privacy", assemble_inner(cfg, "Privacy", format_text(cfg.priv_txt)))
    case "Terms":
        html_to_render = build_page(cfg, "Terms",   assemble_inner(cfg, "Terms",   format_text(cfg.term_txt)))
    case "Blog Index":
        html_to_render = build_page(cfg, "Blog",    templates.gen_blog_index_html(cfg))
    case "Blog Post":
        html_to_render = build_page(cfg, "Article", templates.gen_blog_post_html(cfg))
    case "Product (Demo)":
        st.info("Demo mode: showing first CSV row.")
        html_to_render = build_page(cfg, "Product", templates.gen_product_page_content(cfg, is_demo=True))
    case "Booking":
        html_to_render = build_page(cfg, "Book Now", templates.gen_booking_content(cfg))
    case _:
        html_to_render = build_page(cfg, "Home", assemble_home(cfg))

# Render preview
preview_col, deploy_col = st.columns([3, 1])
with preview_col:
    if device_mode == "📱 Mobile":
        st.markdown("<div style='text-align:center;color:#888;margin-bottom:8px;'><i>📱 iPhone 14 Pro Simulation</i></div>", unsafe_allow_html=True)
        _, phone, _ = st.columns([1.2, 1.5, 1.2])
        with phone:
            st.markdown("""
            <style>.phone-bezel{border:14px solid #1a1a1a;border-radius:40px;background:#000;box-shadow:0 25px 50px -12px rgba(0,0,0,0.5);overflow:hidden;margin:0 auto;}</style>
            <div class="phone-bezel">""", unsafe_allow_html=True)
            st.components.v1.html(html_to_render, height=750, scrolling=True)
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.components.v1.html(html_to_render, height=750, scrolling=True)

with deploy_col:
    st.success("v55 Architecture compiled.")
    zip_buf = build_zip(cfg)

    if cfg.pinata_jwt:
        if st.button("🌌 Push to IPFS", type="primary"):
            with st.spinner("Uploading to IPFS…"):
                try:
                    res = requests.post(
                        "https://api.pinata.cloud/pinning/pinFileToIPFS",
                        headers={"Authorization": f"Bearer {cfg.pinata_jwt}"},
                        files={"file": ("titan_site.zip", zip_buf.getvalue())},
                    )
                    if res.status_code == 200:
                        cid = res.json()['IpfsHash']
                        st.success("Deployed to IPFS!")
                        st.markdown(f"[ipfs.io/ipfs/{cid}](https://ipfs.io/ipfs/{cid})")
                    else:
                        st.error(f"IPFS error: {res.text}")
                except Exception as e:
                    st.error(f"Upload failed: {e}")
    else:
        st.download_button(
            "📥 Download 2050 Package",
            zip_buf.getvalue(),
            f"{cfg.biz_name.lower().replace(' ', '_')}_apex.zip",
            "application/zip",
            type="primary",
        )
