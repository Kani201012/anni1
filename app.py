import streamlit as st
import zipfile
import io
import urllib.parse
import datetime

# --- 1. APP CONFIGURATION ---
st.set_page_config(
    page_title="Titan v27.0 | Kaydiem Professional Architect", 
    layout="wide", 
    page_icon="⚡",
    initial_sidebar_state="expanded"
)

# --- 2. ADVANCED UI SYSTEM (CSS) ---
st.markdown("""
    <style>
    :root { --primary: #0f172a; --accent: #3b82f6; }
    .stApp { background-color: #f8fafc; color: #1e293b; font-family: 'Inter', sans-serif; }
    [data-testid="stSidebar"] h1 { 
        background: linear-gradient(90deg, #0f172a, #3b82f6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 900 !important;
    }
    .stButton>button {
        width: 100%; border-radius: 8px; height: 3.5rem;
        background: linear-gradient(135deg, #0f172a 0%, #2563eb 100%);
        color: white; font-weight: 800; border: none;
        box-shadow: 0 4px 15px rgba(37, 99, 235, 0.3);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SIDEBAR: THE CONTROL CENTER ---
with st.sidebar:
    st.title("Titan Architect")
    st.caption("v27.0 | Professional Edition")
    st.divider()
    
    with st.expander("🎨 Visual DNA", expanded=True):
        theme_mode = st.selectbox("Base Theme", ["Clean Corporate (Light)", "Midnight SaaS (Dark)", "Glassmorphism"])
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
        show_features = st.checkbox("Expertise Cards (Icons)", value=True)
        show_inventory = st.checkbox("Live Inventory (CSV)", value=True)
        show_gallery = st.checkbox("Visual About Section", value=True)
        show_testimonials = st.checkbox("Testimonials", value=True)
        show_faq = st.checkbox("F.A.Q.", value=True)
        show_cta = st.checkbox("Final Call to Action", value=True)

    with st.expander("⚙️ SEO & Technical"):
        gsc_tag = st.text_input("Google Verification ID")
        ga_tag = st.text_input("Google Analytics ID")
        og_image = st.text_input("Social Share Image URL")

# --- 4. MAIN WORKSPACE ---
tabs = st.tabs(["1. Identity", "2. Content Blocks", "3. Inventory", "4. Legal & Footer"])

with tabs[0]:
    c1, c2 = st.columns(2)
    with c1:
        biz_name = st.text_input("Business Name", "Kaydiem Script Lab")
        biz_tagline = st.text_input("Tagline", "Advanced Scripting & Software Architecture")
        biz_phone = st.text_input("Phone", "+91 000 000 0000")
        biz_email = st.text_input("Email", "hello@kaydiemscriptlab.com")
    with c2:
        prod_url = st.text_input("Website URL", "https://www.kaydiemscriptlab.com")
        biz_addr = st.text_area("Address", "Kanishka's House, Garia Station Rd, Kolkata, India", height=100)
        map_iframe = st.text_area("Google Map Embed Code", height=100)
        seo_d = st.text_area("Meta Description", "Leading software laboratory specializing in custom scripts and automation.", height=100)
        logo_url = st.text_input("Logo URL (PNG/SVG)")
        wa_num = st.text_input("WhatsApp (No +)", "910000000000")

with tabs[1]:
    st.subheader("Hero & Proof")
    hero_h = st.text_input("Hero Headline", "Engineering the Future of Automation")
    hero_sub = st.text_area("Hero Subtext", "We build premium scripts and software architecture that stops revenue leakage and fuels growth.")
    hero_img = st.text_input("Hero Background Image", "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?auto=format&fit=crop&q=80&w=1600")
    
    st.subheader("Expertise Grid (Visual Icons)")
    feat_data = st.text_area("Features (Title | Desc | IconURL)", 
                             "Custom Scripting | Fast automation for business. | https://cdn-icons-png.flaticon.com/512/2534/2534063.png\nRevenue Leakage | AI-driven profit protection. | https://cdn-icons-png.flaticon.com/512/2534/2534035.png\nSaaS Labs | Scalable cloud architecture. | https://cdn-icons-png.flaticon.com/512/2103/2103633.png", height=120)
    
    st.subheader("About Content")
    about_h = st.text_input("About Title", "The Kaydiem Legacy")
    about_img = st.text_input("About Image", "https://images.unsplash.com/photo-1522071820081-009f0129c71c?auto=format&fit=crop&q=80&w=1600")
    about_long = st.text_area("Full Story", "**Our Philosophy**\nCode should empower, not just function.")

with tabs[2]:
    sheet_url = st.text_input("Google Sheet CSV Link")
    custom_feat = st.text_input("Default Product Image", "https://images.unsplash.com/photo-1551288049-bebda4e38f71?q=80&w=800")

with tabs[3]:
    testi_data = st.text_area("Testimonials (Name | Quote)", "A. Mehta | Reduced workload by 70%.")
    faq_data = st.text_area("FAQ (Q? ? A)", "Is it secure? ? Yes, 100% encrypted.")
    priv_txt = st.text_area("Privacy Policy", "**Data Policy**\nWe respect your data.")
    term_txt = st.text_area("Terms of Service", "**Usage**\nYou agree to our terms.")

# --- 5. COMPILER ENGINE (FIXING LACKS) ---

def format_text(text):
    if not text: return ""
    return "".join([f"<h3>{p.strip().replace('**','')}</h3>" if p.strip().startswith("**") else f"<p>{p}</p>" for p in text.split('\n')])

def get_theme_css():
    hero_bg = f"background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), url('{hero_img}') !important;"
    return f"""
    :root {{
        --p: {p_color}; --s: {s_color}; --radius: {border_rad};
        --h-font: '{h_font}', sans-serif; --b-font: '{b_font}', sans-serif;
    }}
    body {{ font-family: var(--b-font); margin: 0; line-height: 1.6; color: #1e293b; }}
    h1, h2, h3 {{ font-family: var(--h-font); color: var(--p); line-height: 1.2; }}
    .container {{ max-width: 1200px; margin: 0 auto; padding: 0 20px; }}
    
    /* FIX: Sticky Header */
    nav {{ position: fixed; top: 0; width: 100%; z-index: 1000; background: rgba(255,255,255,0.98); backdrop-filter: blur(10px); padding: 1rem 0; border-bottom: 1px solid #eee; }}
    .nav-flex {{ display: flex; justify-content: space-between; align-items: center; }}
    .nav-links a {{ margin-left: 2rem; text-decoration: none; font-weight: 600; color: #0f172a; font-size: 0.9rem; }}
    
    /* FIX: Hero Visuals */
    .hero {{ min-height: 80vh; display: flex; align-items: center; justify-content: center; text-align: center; {hero_bg} background-size: cover !important; background-position: center !important; color: white; padding-top: 80px; }}
    .hero h1 {{ color: white; font-size: clamp(2.5rem, 5vw, 4rem); }}
    
    .btn {{ display: inline-block; padding: 1rem 2.5rem; border-radius: var(--radius); font-weight: 700; text-decoration: none; transition: 0.3s; cursor: pointer; border: none; }}
    .btn-accent {{ background: var(--s); color: white; box-shadow: 0 10px 20px rgba(0,0,0,0.1); }}
    
    .grid-3 {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 2rem; padding: 4rem 0; }}
    .card {{ background: white; padding: 2.5rem; border-radius: var(--radius); border: 1px solid #f1f5f9; transition: 0.3s; }}
    .card:hover {{ transform: translateY(-5px); box-shadow: 0 20px 40px -10px rgba(0,0,0,0.1); }}
    .card img {{ width: 60px; height: 60px; margin-bottom: 1.5rem; }}

    footer {{ background: var(--p); color: white; padding: 5rem 0 2rem 0; }}
    footer a {{ color: rgba(255,255,255,0.7); text-decoration: none; margin-bottom: 0.5rem; display: block; }}
    
    .reveal {{ opacity: 0; transform: translateY(30px); transition: 0.8s; }}
    .reveal.active {{ opacity: 1; transform: translateY(0); }}
    
    @media (max-width: 768px) {{ .nav-links {{ display: none; }} }}
    """

def gen_nav():
    return f"""<nav><div class="container nav-flex">
        <a href="index.html" style="font-weight:900; font-size:1.5rem; color:var(--p); text-decoration:none;">{biz_name}</a>
        <div class="nav-links">
            <a href="index.html">Home</a>
            <a href="about.html">About</a>
            <a href="contact.html">Contact</a>
            <a href="https://wa.me/{wa_num}" class="btn-accent btn" style="padding:0.6rem 1.2rem; margin-left:1rem;">WhatsApp</a>
        </div>
    </div></nav>"""

def gen_schema():
    return f"""
    <script type="application/ld+json">
    {{
      "@context": "https://schema.org",
      "@type": "SoftwareApplication",
      "name": "{biz_name}",
      "operatingSystem": "Web",
      "applicationCategory": "BusinessApplication",
      "description": "{seo_d}",
      "author": {{ "@type": "Organization", "name": "Kaydiem Script Lab", "url": "{prod_url}" }}
    }}
    </script>"""

def gen_footer():
    return f"""<footer><div class="container">
        <div class="grid-3" style="padding:0;">
            <div><h3>{biz_name}</h3><p style="opacity:0.7;">{biz_addr}</p><p>{biz_phone}</p></div>
            <div><h4>Explore</h4><a href="index.html">Home</a><a href="about.html">Expertise</a><a href="contact.html">Support</a></div>
            <div><h4>Legal</h4><a href="privacy.html">Privacy Policy</a><a href="terms.html">Terms of Service</a></div>
        </div>
        <div style="border-top:1px solid rgba(255,255,255,0.1); margin-top:4rem; padding-top:2rem; text-align:center; font-size:0.85rem;">
            &copy; {datetime.datetime.now().year} <a href="https://www.kaydiemscriptlab.com/" target="_blank" style="display:inline; color:white; text-decoration:underline;">Kaydiem Script Lab</a>. Powered by Titan Engine.
        </div>
    </div></footer>"""

def build_page(title, content, extra_js=""):
    return f"""<!DOCTYPE html><html lang="en"><head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | {biz_name}</title>
    {gen_schema()}
    <style>{get_theme_css()}</style>
    </head><body>{gen_nav()}{content}{gen_footer()}
    <script>
    window.addEventListener('scroll', () => {{
        document.querySelectorAll('.reveal').forEach(el => {{
            if(el.getBoundingClientRect().top < window.innerHeight - 50) el.classList.add('active');
        }});
    }});
    window.dispatchEvent(new Event('scroll'));
    </script>{extra_js}</body></html>"""

# --- INVENTORY JS ---
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
                <img src="${{c[3] || '{custom_feat}'}}" style="width:100%; height:220px; object-fit:cover; border-radius:8px; margin-bottom:1rem;">
                <h3>${{c[0]}}</h3>
                <p style="color:var(--s); font-weight:bold; font-size:1.2rem;">${{c[1]}}</p>
                <p style="font-size:0.9rem; opacity:0.7;">${{c[2].substring(0,80)}}...</p>
                <a href="product.html?item=${{encodeURIComponent(c[0])}}" class="btn btn-accent" style="display:block; text-align:center; margin-top:1rem;">Product Details</a>
            </div>`;
        }}
    }});
}}
window.addEventListener('load', loadInv);
</script>"""

# --- PAGE CONTENT ---
home_content = f"""
<section class="hero"><div class="container reveal">
    <h1>{hero_h}</h1>
    <p>{hero_sub}</p>
    <a href="#inventory" class="btn btn-accent">Explore Solutions</a>
</div></section>
<section class="container"><div class="grid-3" style="padding: 5rem 0;">
    {"".join([f'<div class="card reveal"><img src="{x.split("|")[2].strip() if len(x.split("|"))>2 else "https://cdn-icons-png.flaticon.com/512/1055/1055666.png"}"><h3>{x.split("|")[0]}</h3><p>{x.split("|")[1]}</p></div>' for x in feat_data.split('\\n') if "|" in x])}
</div></section>
<section id="inventory" style="background:#f8fafc;"><div class="container">
    <h2 style="text-align:center; font-size:2.5rem;">Live Solutions Lab</h2>
    <div class="grid-3" id="inv-grid">Loading Laboratory Database...</div>
</div></section>
"""

# --- DOWNLOAD LOGIC ---
st.divider()
if st.button("🚀 DOWNLOAD PROFESSIONAL 2026 SITE ZIP", type="primary"):
    z_b = io.BytesIO()
    with zipfile.ZipFile(z_b, "a", zipfile.ZIP_DEFLATED, False) as zf:
        zf.writestr("index.html", build_page("Home", home_content, inv_js))
        zf.writestr("about.html", build_page("Expertise", f"<section style='padding:150px 0;'><div class='container'><h1>{about_h}</h1>{format_text(about_long)}<img src='{about_img}' style='width:100%; border-radius:12px; margin-top:2rem;'></div></section>"))
        zf.writestr("contact.html", build_page("Contact", f"<section style='padding:150px 0;'><div class='container' style='text-align:center;'><h1>Let's Build Together</h1><p>{biz_addr}</p><h2>{biz_phone}</h2><a href='mailto:{biz_email}' class='btn btn-accent'>{biz_email}</a><br><br>{map_iframe}</div></section>"))
        zf.writestr("product.html", build_page("Detail", "<section style='padding:150px 0;'><div class='container' id='prod-detail'><h1>Loading Data...</h1></div></section>", "<!-- Product JS Logic Here -->"))
        zf.writestr("privacy.html", build_page("Privacy", f"<section style='padding:100px 0;'><div class='container'>{format_text(priv_txt)}</div></section>"))
        zf.writestr("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {prod_url}/sitemap.xml")
        zf.writestr("sitemap.xml", f"<?xml version='1.0' encoding='UTF-8'?><urlset xmlns='http://www.sitemaps.org/schemas/sitemap/0.9'><url><loc>{prod_url}/index.html</loc></url></urlset>")
        zf.writestr("404.html", build_page("404", "<section style='padding:150px 0; text-align:center;'><div class='container'><h1>404</h1><p>The code you are looking for does not exist.</p><a href='index.html' class='btn btn-accent'>Return to Lab</a></div></section>"))

    st.download_button("📥 Save Website", z_b.getvalue(), "kaydiem_pro_v27.zip", "application/zip")
