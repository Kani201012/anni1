import streamlit as st
import zipfile
import io
import urllib.parse
import datetime

# --- 1. APP CONFIGURATION ---
st.set_page_config(
    page_title="Titan v26.6 | Kaydiem Architect", 
    layout="wide", 
    page_icon="⚡",
    initial_sidebar_state="expanded"
)

# --- 2. ADVANCED UI SYSTEM (CSS) ---
st.markdown("""
    <style>
    :root { --primary: #0f172a; --accent: #3b82f6; }
    .stApp { background-color: #f8fafc; color: #1e293b; font-family: 'Inter', sans-serif; }
    [data-testid="stSidebar"] { background-color: #ffffff; border-right: 1px solid #e2e8f0; }
    [data-testid="stSidebar"] h1 { 
        background: linear-gradient(90deg, #0f172a, #3b82f6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 900 !important;
        font-size: 1.8rem !important;
    }
    .stTextInput input, .stTextArea textarea {
        background-color: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 8px !important;
    }
    .stButton>button {
        width: 100%; border-radius: 8px; height: 3.5rem;
        background: linear-gradient(135deg, #0f172a 0%, #2563eb 100%);
        color: white; font-weight: 800; border: none;
        box-shadow: 0 4px 15px rgba(37, 99, 235, 0.3);
        text-transform: uppercase; letter-spacing: 1px;
    }
    iframe { border-radius: 12px; border: 1px solid #e2e8f0; box-shadow: 0 20px 40px -10px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SIDEBAR: THE CONTROL CENTER ---
with st.sidebar:
    st.title("Titan Architect")
    st.caption("v26.6 | Kaydiem Core")
    st.divider()
    
    with st.expander("🎨 Visual DNA", expanded=True):
        theme_mode = st.selectbox("Base Theme", ["Clean Corporate (Light)", "Midnight SaaS (Dark)", "Ocean Breeze", "Stark Minimalist"])
        c1, c2 = st.columns(2)
        p_color = c1.color_picker("Primary Brand", "#0F172A") 
        s_color = c2.color_picker("Action (CTA)", "#3B82F6")  
        h_font = st.selectbox("Headings", ["Space Grotesk", "Montserrat", "Oswald"])
        b_font = st.selectbox("Body Text", ["Inter", "Roboto", "Open Sans"])
        border_rad = st.select_slider("Corner Roundness", ["0px", "8px", "12px", "24px"], value="12px")
        anim_type = st.selectbox("Animation Style", ["Fade Up", "Zoom In", "None"])

    with st.expander("🧩 Section Manager", expanded=False):
        show_hero = st.checkbox("Hero Header", value=True)
        show_stats = st.checkbox("Trust Stats/Logos", value=True)
        show_features = st.checkbox("Feature Grid", value=True)
        show_inventory = st.checkbox("Live Inventory (CSV)", value=True)
        show_gallery = st.checkbox("Visual Gallery (About)", value=True)
        show_testimonials = st.checkbox("Testimonials", value=True)
        show_faq = st.checkbox("F.A.Q.", value=True)
        show_cta = st.checkbox("Final Call to Action", value=True)

    with st.expander("⚙️ SEO & Analytics", expanded=False):
        gsc_tag = st.text_input("Google Verification ID")
        ga_tag = st.text_input("Google Analytics ID (G-XXXX)")
        og_image = st.text_input("Social Share Image URL")

# --- 4. MAIN WORKSPACE ---
tabs = st.tabs(["1. Identity", "2. Content Blocks", "3. Inventory", "4. Legal & Footer"])

with tabs[0]:
    c1, c2 = st.columns(2)
    with c1:
        biz_name = st.text_input("Business Name", "Kaydiem Script Lab")
        biz_tagline = st.text_input("Tagline", "Premium Software & Scripting Solutions")
        biz_phone = st.text_input("Phone", "+91 000 000 0000")
        biz_email = st.text_input("Email", "hello@kaydiemscriptlab.com")
    with c2:
        prod_url = st.text_input("Website URL", "https://www.kaydiemscriptlab.com")
        biz_addr = st.text_area("Address", "Kanishka's House, Garia Station Rd, Kolkata, India", height=100)
        map_iframe = st.text_area("Google Map Embed Code", height=100)
        seo_d = st.text_area("Meta Description (SEO)", "Leading provider of custom scripts and automation solutions.", height=100)
        logo_url = st.text_input("Logo URL")
        wa_num = st.text_input("WhatsApp Number (No +)", "910000000000")

with tabs[1]:
    st.subheader("Hero Section")
    hero_h = st.text_input("Hero Headline", "Empower Your Digital Ecosystem")
    hero_sub = st.text_input("Hero Subtext", "Building the tools that drive modern business automation.")
    hero_img = st.text_input("Hero Background Image URL", "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?auto=format&fit=crop&q=80&w=1600")
    
    st.subheader("Trust Stats")
    col_s1, col_s2, col_s3 = st.columns(3)
    stat_1, label_1 = col_s1.text_input("Stat 1", "10+"), col_s1.text_input("Label 1", "Years")
    stat_2, label_2 = col_s2.text_input("Stat 2", "500+"), col_s2.text_input("Label 2", "Clients")
    stat_3, label_3 = col_s3.text_input("Stat 3", "100%"), col_s3.text_input("Label 3", "Security")

    st.subheader("Feature Grid")
    feat_data = st.text_area("Features (Title | Desc)", "Custom Scripting | Fast automation.\nSaaS Systems | Scalable apps.\n24/7 Support | Always here.", height=100)
    
    st.subheader("About")
    about_h = st.text_input("About Title", "Our Legacy")
    about_img = st.text_input("About Image URL", "https://images.unsplash.com/photo-1522071820081-009f0129c71c?auto=format&fit=crop&q=80&w=1600")
    about_short = st.text_area("Short Summary", "We treat every project as a unique experiment in efficiency.")
    about_long = st.text_area("Full Story", "**Our Philosophy**\nSoftware should empower business...")

with tabs[2]:
    sheet_url = st.text_input("Google Sheet CSV Link")
    custom_feat = st.text_input("Default Product Image", "https://images.unsplash.com/photo-1551288049-bebda4e38f71?q=80&w=800")

with tabs[3]:
    testi_data = st.text_area("Testimonials (Name | Quote)", "Mehta | Reduced workload by 70%.")
    faq_data = st.text_area("FAQ (Q? ? A)", "Is it secure? ? Yes, encrypted.")
    priv_txt = st.text_area("Privacy Policy", "**Introduction**\nWe value your data...")
    term_txt = st.text_area("Terms of Service", "**Usage**\nBy using this site...")

# --- 5. COMPILER ENGINE ---

def format_text(text):
    if not text: return ""
    paragraphs = text.split('\n')
    html_out = ""
    for p in paragraphs:
        if p.strip().startswith("**") and p.strip().endswith("**"):
            html_out += f"<h3 style='color:var(--p);'>{p.strip().replace('**','')}</h3>"
        else:
            html_out += f"<p style='opacity:0.8;'>{p}</p>"
    return html_out

def get_theme_css():
    anim_css = ".reveal { opacity: 0; transform: translateY(30px); transition: all 0.8s ease-out; } .reveal.active { opacity: 1; transform: translateY(0); }" if anim_type != "None" else ""
    # FIX: Hero Image background-image logic
    hero_bg = f"background: linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.6)), url('{hero_img}') !important;" if hero_img else "background: var(--p);"
    
    return f"""
    :root {{
        --p: {p_color}; --s: {s_color}; --radius: {border_rad};
        --h-font: '{h_font}', sans-serif; --b-font: '{b_font}', sans-serif;
    }}
    body {{ font-family: var(--b-font); margin: 0; line-height: 1.6; overflow-x: hidden; }}
    h1, h2, h3 {{ font-family: var(--h-font); color: var(--p); }}
    .container {{ max-width: 1200px; margin: 0 auto; padding: 0 20px; }}
    nav {{ position: fixed; top: 0; width: 100%; z-index: 1000; background: rgba(255,255,255,0.95); backdrop-filter: blur(10px); padding: 1rem 0; border-bottom: 1px solid #eee; }}
    .nav-flex {{ display: flex; justify-content: space-between; align-items: center; }}
    .hero {{ min-height: 80vh; display: flex; align-items: center; justify-content: center; text-align: center; {hero_bg} background-size: cover !important; background-position: center !important; color: white; padding-top: 80px; }}
    .btn {{ display: inline-block; padding: 0.8rem 2rem; border-radius: var(--radius); text-decoration: none; font-weight: 700; transition: 0.3s; }}
    .btn-accent {{ background: var(--s); color: white; }}
    .grid-3 {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 2rem; }}
    .card {{ background: white; padding: 2rem; border-radius: var(--radius); border: 1px solid #eee; height: 100%; transition: 0.3s; }}
    footer {{ background: var(--p); color: white; padding: 4rem 0; margin-top: 4rem; }}
    footer a {{ color: rgba(255,255,255,0.7); text-decoration: none; }}
    {anim_css}
    """

def gen_nav():
    return f"""<nav><div class="container nav-flex">
        <a href="index.html" style="font-weight:900; font-size:1.5rem; color:var(--p); text-decoration:none;">{biz_name}</a>
        <div style="display:flex; gap:1.5rem; align-items:center;">
            <a href="index.html" style="text-decoration:none; color:var(--primary); font-weight:600;">Home</a>
            <a href="about.html" style="text-decoration:none; color:var(--primary); font-weight:600;">About</a>
            <a href="contact.html" style="text-decoration:none; color:var(--primary); font-weight:600;">Contact</a>
            <a href="https://wa.me/{wa_num}" class="btn btn-accent" style="padding:0.5rem 1rem;">WhatsApp</a>
        </div>
    </div></nav>"""

def gen_footer():
    return f"""<footer><div class="container">
        <div class="grid-3">
            <div><h3>{biz_name}</h3><p>{biz_addr}</p></div>
            <div><h4>Quick Links</h4><a href="index.html">Home</a><br><a href="about.html">About</a><br><a href="contact.html">Contact</a></div>
            <div><h4>Legal</h4><a href="privacy.html">Privacy</a><br><a href="terms.html">Terms</a></div>
        </div>
        <div style="border-top:1px solid rgba(255,255,255,0.1); margin-top:2rem; padding-top:2rem; text-align:center;">
            &copy; <a href="https://www.kaydiemscriptlab.com/" target="_blank" style="color:white; text-decoration:underline;">Kaydiem Script Lab</a>. Powered by Titan Engine.
        </div>
    </div></footer>"""

# --- PAGE COMPILERS ---

def build_page(title, content, extra_js=""):
    return f"""<!DOCTYPE html><html lang="en"><head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | {biz_name}</title>
    <style>{get_theme_css()}</style>
    </head><body>{gen_nav()}{content}{gen_footer()}
    <script>
    window.addEventListener('scroll', () => {{
        document.querySelectorAll('.reveal').forEach(el => {{
            if(el.getBoundingClientRect().top < window.innerHeight - 100) el.classList.add('active');
        }});
    }});
    </script>{extra_js}</body></html>"""

# --- INVENTORY & PRODUCT DETAIL JS ---
inv_js = f"""<script>
async function loadInv() {{
    const res = await fetch('{sheet_url}');
    const txt = await res.text();
    const lines = txt.split('\\n').slice(1);
    const box = document.getElementById('inv-grid');
    if(!box) return; box.innerHTML = '';
    lines.forEach(line => {{
        const c = line.split(',');
        if(c.length > 1) {{
            box.innerHTML += `
            <div class="card reveal">
                <img src="${{c[3] || '{custom_feat}'}}" style="width:100%; height:200px; object-fit:cover; border-radius:8px;">
                <h3>${{c[0]}}</h3>
                <p style="color:var(--s); font-weight:bold;">${{c[1]}}</p>
                <a href="product.html?item=${{encodeURIComponent(c[0])}}" class="btn btn-accent" style="display:block; text-align:center;">View Details</a>
            </div>`;
        }}
    }});
}}
window.addEventListener('load', loadInv);
</script>"""

product_detail_page = f"""
<section style="padding:150px 0;"><div class="container" id="detail-box"><h1>Loading Product...</h1></div></section>
<script>
async function loadDetail() {{
    const name = new URLSearchParams(window.location.search).get('item');
    const res = await fetch('{sheet_url}');
    const txt = await res.text();
    const lines = txt.split('\\n');
    lines.forEach(line => {{
        const c = line.split(',');
        if(c[0] === name) {{
            document.getElementById('detail-box').innerHTML = `
            <div class="grid-3" style="grid-template-columns: 1fr 1fr;">
                <img src="${{c[3] || '{custom_feat}'}}" style="width:100%; border-radius:12px;">
                <div>
                    <h1>${{c[0]}}</h1>
                    <h2 style="color:var(--s);">${{c[1]}}</h2>
                    <p>${{c[2]}}</p>
                    <a href="https://wa.me/{wa_num}?text=Interested in ${{c[0]}}" class="btn btn-accent">Order via WhatsApp</a>
                </div>
            </div>`;
        }}
    }});
}}
window.addEventListener('load', loadDetail);
</script>"""

# --- APP RENDER ---
home_content = f"""
<section class="hero"><div class="container reveal"><h1>{hero_h}</h1><p>{hero_sub}</p></div></section>
<section style="padding:5rem 0;"><div class="container"><div class="grid-3" id="inv-grid">Loading Products...</div></div></section>
"""

st.subheader("🚀 Launchpad")
if st.button("DOWNLOAD WEBSITE ZIP", type="primary"):
    z_b = io.BytesIO()
    with zipfile.ZipFile(z_b, "a", zipfile.ZIP_DEFLATED, False) as zf:
        zf.writestr("index.html", build_page("Home", home_content, inv_js))
        zf.writestr("product.html", build_page("Product Detail", product_detail_page))
        zf.writestr("about.html", build_page("About", f"<section style='padding:150px 0;'><div class='container'><h1>{about_h}</h1>{format_text(about_long)}</div></section>"))
        zf.writestr("contact.html", build_page("Contact", f"<section style='padding:150px 0;'><div class='container'><h1>Contact</h1><p>{biz_addr}</p>{map_iframe}</div></section>"))
        zf.writestr("privacy.html", build_page("Privacy", f"<section style='padding:100px 0;'><div class='container'>{format_text(priv_txt)}</div></section>"))
        zf.writestr("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {prod_url}/sitemap.xml")
        zf.writestr("sitemap.xml", f"<?xml version='1.0' encoding='UTF-8'?><urlset xmlns='http://www.sitemaps.org/schemas/sitemap/0.9'><url><loc>{prod_url}/index.html</loc></url></urlset>")
        zf.writestr("404.html", build_page("404", "<section style='padding:150px 0; text-align:center;'><div class='container'><h1>404</h1><p>Not Found</p></div></section>"))

    st.download_button("📥 Click to Save", z_b.getvalue(), "kaydiem_site.zip", "application/zip")

st.info("Check Tab 1-4 to fill your company data before downloading.")
